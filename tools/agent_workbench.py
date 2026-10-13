"""本地协作工作台：任务认领、接力、角色反馈、封存调研与人工看板；仅用标准库。"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import sqlite3
import subprocess
import sys
import time
from urllib.parse import urlparse


ROLES = {"developer", "tester", "researcher", "integrator", "human"}
KINDS = {"development": "developer", "test": "tester",
         "research": "researcher", "integration": "integrator"}
MODES = {"serial", "collaborative", "independent_compare"}


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value):
        raise ValueError("ID 只能含字母、数字、下划线和连字符，最长 64 字符")
    return value


def dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def utc():
    return datetime.now(timezone.utc).isoformat()


def text(value, label="内容"):
    if not isinstance(value, str) or not value.strip() or len(value) > 64000:
        raise ValueError(label + "须为 1～64000 字符")
    return value


def overlap(left, right):
    # 目录本身与后代都占用同一范围；不能只比较字符串是否完全相等。
    return left == right or left == "." or right == "." or (
        left.startswith(right + "/") or right.startswith(left + "/"))


SCHEMA = """
CREATE TABLE IF NOT EXISTS agents(
 id TEXT PRIMARY KEY, client TEXT NOT NULL, roles TEXT NOT NULL, state TEXT NOT NULL,
 command TEXT NOT NULL, quota_codes TEXT NOT NULL, workspace TEXT NOT NULL,
 foreground INTEGER NOT NULL, seen REAL NOT NULL);
CREATE TABLE IF NOT EXISTS tasks(
 id TEXT PRIMARY KEY, title TEXT NOT NULL, kind TEXT NOT NULL, mode TEXT NOT NULL,
 status TEXT NOT NULL, owner TEXT, epoch INTEGER NOT NULL DEFAULT 0, scopes TEXT NOT NULL,
 dependencies TEXT NOT NULL, subject TEXT, contract TEXT NOT NULL, checkpoint TEXT NOT NULL,
 result TEXT NOT NULL, developers TEXT NOT NULL, backups TEXT NOT NULL, run_id TEXT, slot TEXT);
CREATE TABLE IF NOT EXISTS messages(
 id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT NOT NULL, recipient TEXT NOT NULL,
 task TEXT NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL, seen INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS runs(
 id TEXT PRIMARY KEY, question TEXT NOT NULL, criteria TEXT NOT NULL, participants TEXT NOT NULL,
 integrator TEXT NOT NULL, closed INTEGER NOT NULL DEFAULT 0, summary TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS reports(
 run TEXT NOT NULL, agent TEXT NOT NULL, author TEXT NOT NULL, report TEXT NOT NULL, PRIMARY KEY(run,agent));
CREATE TABLE IF NOT EXISTS events(
 id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, item TEXT NOT NULL,
 detail TEXT NOT NULL, created TEXT NOT NULL);
"""


class Workbench:
    def __init__(self, root):
        self.root = Path(root).resolve()
        if not (self.root / ".agents/PROTOCOL.md").is_file():
            raise ValueError("--root 必须指向已有协议的唯一主协作目录")
        # 复用已有忽略目录，但与旧 relay 数据库分开，避免迁移旧消息。
        self.directory = self.root / ".agent-relay/workbench"
        if not self.directory.resolve().is_relative_to(self.root):
            raise ValueError("运行目录不能逃逸主协作目录")
        self.db = self.directory / "state.sqlite3"

    @contextmanager
    def connection(self, write=False):
        if not self.directory.resolve().is_relative_to(self.root) or not self.db.resolve().is_relative_to(self.root):
            raise ValueError("运行目录或数据库指向工程外")
        self.directory.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db, timeout=20, isolation_level=None)
        conn.row_factory = sqlite3.Row
        try:
            if conn.execute("PRAGMA user_version").fetchone()[0] > 2:
                raise ValueError("运行数据库版本较新，拒绝修改")
            conn.executescript(SCHEMA)
            if conn.execute("PRAGMA user_version").fetchone()[0] < 2:
                # 原型迭代也保留已有登记、检查点和首稿；迁移本身同样串行。
                conn.execute("BEGIN IMMEDIATE")
                columns = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}
                for column in ("run_id", "slot"):
                    if column not in columns:
                        conn.execute("ALTER TABLE tasks ADD COLUMN " + column + " TEXT")
                columns = {row["name"] for row in conn.execute("PRAGMA table_info(reports)")}
                if "author" not in columns:
                    conn.execute("ALTER TABLE reports ADD COLUMN author TEXT NOT NULL DEFAULT ''")
                    conn.execute("UPDATE reports SET author=agent")
                conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS one_research_slot ON tasks(run_id,slot) "
                             "WHERE run_id IS NOT NULL")
                conn.execute("PRAGMA user_version=2")
                conn.commit()
            # 认领、冲突检测、编号和通知在同一事务中完成，杜绝先读后写竞态。
            conn.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()

    def scope(self, value):
        if not isinstance(value, str) or "\\" in value or ":" in value:
            raise ValueError("scope 使用工程相对路径和正斜杠")
        path = PurePosixPath(value)
        if not value or path.is_absolute() or ".." in path.parts or path.parts[:1] == (".git",):
            raise ValueError("非法 scope")
        if not (self.root / value).resolve().is_relative_to(self.root):
            raise ValueError("scope 逃逸工程")
        result = path.as_posix()
        return result.casefold() if os.name == "nt" else result

    @staticmethod
    def event(conn, kind, item, detail):
        conn.execute("INSERT INTO events(kind,item,detail,created) VALUES(?,?,?,?)",
                     (kind, item, detail, utc()))

    @staticmethod
    def row(conn, table, key):
        result = conn.execute("SELECT * FROM " + table + " WHERE id=?", (identifier(key),)).fetchone()
        if result is None:
            raise ValueError(table + " 中没有 " + key)
        return dict(result)

    @staticmethod
    def message(conn, sender, recipient, task, body):
        cursor = conn.execute(
            "INSERT INTO messages(sender,recipient,task,body,created) VALUES(?,?,?,?,?)",
            (sender, recipient, task, body, utc()))
        return cursor.lastrowid

    def join(self, agent, client, roles, command=None, quota_codes=None, workspace=None, foreground=False):
        identifier(agent)
        text(client, "客户端")
        if not isinstance(roles, list) or not roles or not set(roles) <= ROLES:
            raise ValueError("roles 必须包含有效角色")
        command = [] if command is None else command
        quota_codes = [] if quota_codes is None else quota_codes
        if not isinstance(command, list) or any(not isinstance(x, str) or not x for x in command):
            raise ValueError("command 是参数数组，不是 shell 字符串")
        if not isinstance(quota_codes, list) or any(type(x) is not int or x == 0 for x in quota_codes):
            raise ValueError("quota_codes 是适配器明确约定的非零退出码")
        if type(foreground) is not bool:
            raise ValueError("foreground 必须明确说明退出后是否所有写者均已停止")
        location = str(Path(workspace or self.root).resolve())
        if not Path(location).is_dir():
            raise ValueError("工作目录不存在")
        with self.connection(True) as conn:
            if conn.execute("SELECT 1 FROM agents WHERE id=?", (agent,)).fetchone():
                raise ValueError("会话 ID 已登记；不同实例必须使用不同 ID")
            conn.execute("INSERT INTO agents VALUES(?,?,?,?,?,?,?,?,?)",
                         (agent, client, dump(roles), "available", dump(command),
                          dump(quota_codes), location, int(foreground), time.time()))
            self.event(conn, "join", agent, "登记：" + client)
        return {"agent": agent, "transport": "command" if command else "manual"}

    def heartbeat(self, agent):
        with self.connection(True) as conn:
            self.row(conn, "agents", agent)
            conn.execute("UPDATE agents SET seen=? WHERE id=?", (time.time(), agent))
        return {"ok": True}

    def availability(self, agent, state):
        if state not in {"available", "paused", "quota_exhausted"}:
            raise ValueError("未知可用状态")
        with self.connection(True) as conn:
            self.row(conn, "agents", agent)
            conn.execute("UPDATE agents SET state=?,seen=? WHERE id=?", (state, time.time(), agent))
            self.event(conn, "availability", agent, state)
        return {"ok": True}

    def create_task(self, task, title, kind, scopes, contract, dependencies=None,
                    subject=None, mode="collaborative", backups=None, run=None, slot=None):
        identifier(task)
        text(title, "标题")
        text(contract, "公共契约或测试计划")
        if kind not in KINDS or mode not in MODES or mode == "independent_compare":
            raise ValueError("任务使用 serial/collaborative；独立对照使用 create_run")
        if not isinstance(scopes, list):
            raise ValueError("scopes 必须是路径数组；只读任务可为空")
        scopes = list(dict.fromkeys(self.scope(x) for x in scopes))
        dependencies = list(dict.fromkeys(dependencies or []))
        backups = list(dict.fromkeys(backups or []))
        with self.connection(True) as conn:
            for dependency in dependencies:
                self.row(conn, "tasks", dependency)
            for backup in backups:
                self.row(conn, "agents", backup)
            if kind == "test":
                implementation = self.row(conn, "tasks", subject)
                if implementation["kind"] != "development":
                    raise ValueError("测试 subject 必须是开发任务")
                if implementation["status"] == "done":
                    raise ValueError("已验收开发任务需要新建修订任务，不能事后追加验收门槛")
                if subject not in dependencies:
                    dependencies.append(subject)
            elif subject is not None:
                raise ValueError("只有测试任务使用 subject")
            if run is not None:
                research = self.row(conn, "runs", run)
                members = json.loads(research["participants"])
                if kind != "research" or research["closed"] or slot not in members:
                    raise ValueError("调研任务须绑定开放轮次中已有的候选 slot")
                if conn.execute("SELECT 1 FROM reports WHERE run=? AND agent=?", (run, slot)).fetchone():
                    raise ValueError("已有首稿的候选不能重新建任务覆盖")
                if any(x in members and x != slot for x in backups):
                    raise ValueError("同轮次另一候选参与者不能兼任本候选的备用作者")
                contract = research["question"] + "\n比较标准：" + research["criteria"]
            elif slot is not None:
                raise ValueError("slot 需要关联 run")
            conn.execute(
                "INSERT INTO tasks(id,title,kind,mode,status,scopes,dependencies,subject,contract,"
                "checkpoint,result,developers,backups,run_id,slot) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (task, title, kind, mode, "todo", dump(scopes), dump(dependencies), subject,
                 contract, "{}", "{}", "[]", dump(backups), run, slot))
            self.event(conn, "create", task, title)
        return {"task": task}

    def _claim(self, conn, task, agent):
        item = self.row(conn, "tasks", task)
        actor = self.row(conn, "agents", agent)
        roles = json.loads(actor["roles"])
        if actor["state"] != "available" or (KINDS[item["kind"]] not in roles and "human" not in roles):
            raise ValueError("会话不可用或职责不匹配")
        if item["status"] != "todo" or item["owner"]:
            raise ValueError("任务已被领取或当前不可执行")
        if conn.execute("SELECT 1 FROM tasks WHERE owner=?", (agent,)).fetchone():
            raise ValueError("此会话已有在途任务")
        if item["subject"]:
            subject = self.row(conn, "tasks", item["subject"])
            if agent in json.loads(subject["developers"]):
                raise ValueError("开发过此功能的会话不能测试同一功能")
        if item["run_id"]:
            research = self.row(conn, "runs", item["run_id"])
            if research["closed"]:
                raise ValueError("调研轮次已关闭")
            if agent in json.loads(research["participants"]) and agent != item["slot"]:
                raise ValueError("同一实例不能完成本轮的两个独立候选")
            for other in conn.execute("SELECT developers FROM tasks WHERE run_id=? AND slot<>?",
                                      (item["run_id"], item["slot"])):
                if agent in json.loads(other["developers"]):
                    raise ValueError("同一实例已经参与本轮另一独立候选")
            if conn.execute("SELECT 1 FROM reports WHERE run=? AND author=? AND agent<>?",
                            (item["run_id"], agent, item["slot"])).fetchone():
                raise ValueError("同一实例已经提交本轮另一独立候选")
        for dependency in json.loads(item["dependencies"]):
            prior = self.row(conn, "tasks", dependency)
            allowed = {"awaiting_review"} if dependency == item["subject"] else {"done"}
            if prior["status"] not in allowed:
                raise ValueError("依赖尚未交付：" + dependency)
        scopes = json.loads(item["scopes"])
        # stopping 仍持有 owner；没有确认停写之前不能释放它占用的范围。
        for prior in conn.execute("SELECT id,scopes,mode FROM tasks WHERE owner IS NOT NULL"):
            if item["mode"] == "serial" or prior["mode"] == "serial":
                raise ValueError("串行任务正在占用执行阶段")
            if any(overlap(a, b) for a in scopes for b in json.loads(prior["scopes"])):
                raise ValueError("修改范围与任务 " + prior["id"] + " 重叠")
        epoch = item["epoch"] + 1
        developers = json.loads(item["developers"])
        # 同一历史字段也追踪调研接手者，避免一个备用会话先后做两个独立候选。
        if (item["kind"] == "development" or item["run_id"]) and agent not in developers:
            developers.append(agent)
        conn.execute("UPDATE tasks SET owner=?,epoch=?,status='active',developers=? WHERE id=?",
                     (agent, epoch, dump(developers), task))
        conn.execute("UPDATE agents SET seen=? WHERE id=?", (time.time(), agent))
        self.event(conn, "claim", task, agent + " epoch=" + str(epoch))
        return {"task": task, "agent": agent, "epoch": epoch}

    def claim(self, task, agent):
        with self.connection(True) as conn:
            return self._claim(conn, task, agent)

    def _owned(self, conn, task, agent, epoch):
        item = self.row(conn, "tasks", task)
        # 代次是写入栅栏；旧执行者恢复后不能再提交检查点或完成结果。
        if item["owner"] != agent or item["epoch"] != epoch or item["status"] != "active":
            raise ValueError("认领已失效或任务正在停止；核对 owner 与 epoch")
        return item

    def context(self, task, agent):
        with self.connection() as conn:
            item = self.row(conn, "tasks", task)
            if item["owner"] != agent:
                raise ValueError("只向实际领取者提供任务上下文")
            result = {key: item[key] for key in ("id", "title", "kind", "mode", "epoch", "contract")}
            result["checkpoint"] = json.loads(item["checkpoint"])
            result["scopes"] = json.loads(item["scopes"])
            pending = json.loads(item["result"]).get("pending_adapter_result")
            if pending is not None:
                result["pending_result"] = pending
            if item["subject"]:
                subject = self.row(conn, "tasks", item["subject"])
                result["implementation"] = {"task": subject["id"], "contract": subject["contract"],
                                            "result": json.loads(subject["result"])}
            if item["run_id"]:
                result.update(run=item["run_id"], slot=item["slot"])
            # 不注入其他 Agent 完整对话、候选首稿或隐藏测试计划。
            return result

    def checkpoint(self, task, agent, epoch, data):
        if not isinstance(data, dict) or len(dump(data)) > 64000:
            raise ValueError("checkpoint 必须是小型 JSON 对象")
        with self.connection(True) as conn:
            self._owned(conn, task, agent, epoch)
            conn.execute("UPDATE tasks SET checkpoint=? WHERE id=?", (dump(data), task))
            self.event(conn, "checkpoint", task, agent)
        return {"ok": True}

    def finish(self, task, agent, epoch, result):
        if not isinstance(result, dict) or len(dump(result)) > 64000:
            raise ValueError("result 必须是 JSON 对象")
        with self.connection(True) as conn:
            item = self._owned(conn, task, agent, epoch)
            status = "done"
            if item["kind"] == "development":
                text(result.get("revision"), "待测试的版本")
                status = "awaiting_review"
                # 新版本提交后旧测试结论不再适用，需要重新领取验收。
                conn.execute("UPDATE tasks SET status='todo',result='{}' WHERE subject=? AND owner IS NULL",
                             (task,))
            if item["kind"] == "test":
                subject = self.row(conn, "tasks", item["subject"])
                if subject["owner"] or subject["status"] != "awaiting_review":
                    raise ValueError("开发版本尚未封存或已改变")
                revision = json.loads(subject["result"]).get("revision")
                if result.get("revision") != revision or type(result.get("passed")) is not bool:
                    raise ValueError("测试必须指明相同 revision 和布尔 passed")
                text(result.get("feedback"), "测试反馈")
                if agent in json.loads(subject["developers"]):
                    raise ValueError("不能验收自己开发过的功能")
                # 所有关联测试都结束才解封该版本，避免首个结果让其他在途测试失效。
                peers = list(conn.execute("SELECT status,result FROM tasks WHERE subject=? AND id<>?",
                                          (subject["id"], task)))
                finished = all(peer["status"] == "done" and
                               json.loads(peer["result"]).get("revision") == revision for peer in peers)
                passed = result["passed"] and all(json.loads(peer["result"]).get("passed") is True
                                                   for peer in peers)
                subject_status = ("done" if passed else "todo") if finished else "awaiting_review"
                conn.execute("UPDATE tasks SET status=? WHERE id=?", (subject_status, subject["id"]))
                # 隐藏用例留在测试任务；反馈路由只发送显式复现和结论。
                public = {key: result[key] for key in ("revision", "passed", "feedback")}
                for developer in json.loads(subject["developers"]):
                    self.message(conn, agent, developer, subject["id"], dump(public))
            if item["run_id"]:
                self._save_report(conn, item["run_id"], item["slot"], agent, result.get("report"))
            conn.execute("UPDATE tasks SET owner=NULL,status=?,result=? WHERE id=?",
                         (status, dump(result), task))
            self.event(conn, "finish", task, agent + " -> " + status)
        return {"status": status}

    def stop(self, task, reason, stopped=False, expected_agent=None, expected_epoch=None):
        if reason not in {"quota_exhausted", "paused", "adapter_error", "manual_takeover"}:
            raise ValueError("使用明确错误分类，不能把任意 429 当作额度耗尽")
        if type(stopped) is not bool:
            raise ValueError("stopped 必须是布尔值")
        with self.connection(True) as conn:
            item = self.row(conn, "tasks", task)
            if expected_agent is not None and (item["owner"] != expected_agent or item["epoch"] != expected_epoch):
                raise ValueError("旧适配器代次已失效，不能停止当前执行者")
            if item["status"] not in {"active", "stopping"} or not item["owner"]:
                raise ValueError("没有需要停止的在途执行者")
            previous = item["owner"]
            if reason == "quota_exhausted":
                conn.execute("UPDATE agents SET state='quota_exhausted' WHERE id=?", (previous,))
            # 外部监督者确认进程停止后才释放。心跳过期不触发这一动作。
            conn.execute("UPDATE tasks SET status=?,owner=?,epoch=epoch+1 WHERE id=?",
                         ("todo" if stopped else "stopping", None if stopped else previous, task))
            self.event(conn, "stop", task, reason + "; stopped=" + str(stopped) + "; previous=" + previous)
            backups = json.loads(item["backups"])
            if stopped:
                for backup in backups:
                    self.message(conn, "workbench", backup, task,
                                 "可接力任务 " + task + "；读取 context 的最新检查点后继续。原因：" + reason)
        return {"status": "todo" if stopped else "stopping", "backups": backups}

    def takeover(self, task, agent, stopped):
        if stopped is not True:
            raise ValueError("人工接手前须明确确认原执行者已停止")
        # 在同一事务撤销旧代次并认领，不能在两次调用之间被别人插队。
        with self.connection(True) as conn:
            item = self.row(conn, "tasks", task)
            if item["owner"]:
                conn.execute("UPDATE tasks SET owner=NULL,status='todo',epoch=epoch+1 WHERE id=?", (task,))
            if item["status"] in {"done", "awaiting_review"}:
                raise ValueError("已交付任务请创建修订任务")
            result = self._claim(conn, task, agent)
            self.event(conn, "takeover", task, "人工确认停写，交给 " + agent)
            return result

    def send(self, sender, recipient, task, body):
        text(body, "消息")
        with self.connection(True) as conn:
            self.row(conn, "agents", sender)
            self.row(conn, "agents", recipient)
            self.row(conn, "tasks", task)
            for run in conn.execute("SELECT * FROM runs WHERE closed=0"):
                members = set(json.loads(run["participants"]))
                members.update(row[0] for row in conn.execute(
                    "SELECT owner FROM tasks WHERE run_id=? AND owner IS NOT NULL", (run["id"],)))
                # 交稿或接力后 owner 会清空，历史作者仍受本轮封存约束。
                members.update(row[0] for row in conn.execute(
                    "SELECT author FROM reports WHERE run=?", (run["id"],)))
                for row in conn.execute("SELECT developers FROM tasks WHERE run_id=?", (run["id"],)):
                    members.update(json.loads(row[0]))
                if sender in members and (recipient in members or recipient == run["integrator"]):
                    raise ValueError("调研首稿封存阶段不转发参与者之间的自由文本")
            return {"id": self.message(conn, sender, recipient, task, body)}

    def inbox(self, agent):
        with self.connection() as conn:
            self.row(conn, "agents", agent)
            return [dict(row) for row in conn.execute(
                "SELECT * FROM messages WHERE recipient=? AND seen=0 ORDER BY id", (agent,))]

    def ack(self, agent, message):
        with self.connection(True) as conn:
            row = conn.execute("SELECT * FROM messages WHERE id=?", (message,)).fetchone()
            if row is None or row["recipient"] != agent:
                raise ValueError("消息不存在或收件人不匹配")
            conn.execute("UPDATE messages SET seen=1 WHERE id=?", (message,))
        return {"ok": True}

    def create_run(self, run, question, criteria, participants, integrator):
        identifier(run)
        text(question, "公共问题")
        text(criteria, "比较标准与基线")
        if not isinstance(participants, list) or not participants or len(set(participants)) != len(participants):
            raise ValueError("参与者必须是非空且不重复的列表")
        with self.connection(True) as conn:
            for participant in participants:
                actor = self.row(conn, "agents", participant)
                if "researcher" not in json.loads(actor["roles"]):
                    raise ValueError("调研参与者需要 researcher 角色")
            actor = self.row(conn, "agents", integrator)
            if not set(json.loads(actor["roles"])) & {"integrator", "human"}:
                raise ValueError("汇总者需要 integrator 或 human 角色")
            conn.execute("INSERT INTO runs(id,question,criteria,participants,integrator) VALUES(?,?,?,?,?)",
                         (run, question, criteria, dump(participants), integrator))
            self.event(conn, "run", run, "固定输入；指定汇总者 " + integrator)
        return {"run": run}

    def _save_report(self, conn, run, slot, author, report):
        if not isinstance(report, dict) or not isinstance(report.get("claims"), list) or not report["claims"]:
            raise ValueError("报告须含非空 claims，逐项标记事实／推断／建议和来源")
        for claim in report["claims"]:
            if not isinstance(claim, dict) or claim.get("kind") not in {"fact", "inference", "proposal"}:
                raise ValueError("claim.kind 使用 fact/inference/proposal")
            text(claim.get("statement"), "结论")
            sources = claim.get("sources")
            if not isinstance(sources, list) or (claim["kind"] == "fact" and not sources):
                raise ValueError("事实必须附来源数组")
            if any(not isinstance(x, str) or not x.strip() for x in sources):
                raise ValueError("来源须是非空 URL／文件引用")
        if len(dump(report)) > 64000:
            raise ValueError("报告过大")
        item = self.row(conn, "runs", run)
        if item["closed"] or slot not in json.loads(item["participants"]):
            raise ValueError("轮次已关闭或不是候选 slot")
        # 老数据库 ALTER 后列顺序不同，始终显式指明列名。
        conn.execute("INSERT INTO reports(run,agent,author,report) VALUES(?,?,?,?)",
                     (run, slot, author, dump(report)))
        self.event(conn, "report", run, author + " 已提交候选 " + slot + "；不公开正文")

    def submit_report(self, run, agent, report):
        with self.connection(True) as conn:
            if conn.execute("SELECT 1 FROM tasks WHERE run_id=? AND slot=?", (run, agent)).fetchone():
                raise ValueError("已绑定接力任务的候选通过 finish 提交，防止旧作者抢写")
            self._save_report(conn, run, agent, agent, report)
        return {"submitted": True}

    def view_run(self, run, agent):
        with self.connection() as conn:
            self.row(conn, "agents", agent)
            item = self.row(conn, "runs", run)
            reports = {row["agent"]: json.loads(row["report"]) | {"author": row["author"]} for row in
                       conn.execute("SELECT * FROM reports WHERE run=?", (run,))}
            members = json.loads(item["participants"])
            involved = any(report["author"] == agent for report in reports.values()) or conn.execute(
                "SELECT 1 FROM tasks WHERE run_id=? AND owner=?", (run, agent)).fetchone()
            if agent not in members and agent != item["integrator"] and not involved:
                raise ValueError("不是轮次参与者或指定汇总者")
            # 收齐首稿后仍需人/汇总者明确关闭，避免中途自然暴露候选答案。
            visible = reports if item["closed"] else {
                slot: report for slot, report in reports.items() if report["author"] == agent}
            return {"id": run, "question": item["question"], "criteria": item["criteria"],
                    "integrator": item["integrator"], "closed": bool(item["closed"]),
                    "submitted": list(reports), "missing": [x for x in members if x not in reports],
                    "reports": visible, "summary": item["summary"]}

    def close_run(self, run, actor, allow_missing=False):
        with self.connection(True) as conn:
            item = self.row(conn, "runs", run)
            person = self.row(conn, "agents", actor)
            if actor != item["integrator"] and "human" not in json.loads(person["roles"]):
                raise ValueError("只有指定汇总者或人可关闭轮次")
            submitted = {row[0] for row in conn.execute("SELECT agent FROM reports WHERE run=?", (run,))}
            missing = set(json.loads(item["participants"])) - submitted
            if missing and allow_missing is not True:
                raise ValueError("尚有未提交参与者；人工截止须显式 allow_missing")
            if missing and "human" not in json.loads(person["roles"]):
                raise ValueError("提前截止由人确认")
            conn.execute("UPDATE runs SET closed=1 WHERE id=?", (run,))
            self.event(conn, "close_run", run, "未交付：" + dump(sorted(missing)))
        return {"closed": True, "missing": sorted(missing)}

    def synthesize(self, run, agent, summary):
        text(summary, "汇总")
        with self.connection(True) as conn:
            item = self.row(conn, "runs", run)
            if item["integrator"] != agent or not item["closed"]:
                raise ValueError("关闭轮次后由指定汇总者提交汇总")
            conn.execute("UPDATE runs SET summary=? WHERE id=?", (summary, run))
            self.event(conn, "synthesize", run, agent)
        return {"ok": True}

    def status(self):
        if not self.db.exists():
            return {"agents": [], "tasks": [], "runs": [], "events": []}
        with self.connection() as conn:
            agents = []
            for row in conn.execute("SELECT * FROM agents ORDER BY id"):
                item = dict(row)
                agents.append({key: item[key] for key in ("id", "client", "state")} | {
                    "roles": json.loads(item["roles"]), "last_seen_seconds": round(time.time() - item["seen"]),
                    "transport": "command" if json.loads(item["command"]) else "manual"})
            tasks = []
            for row in conn.execute("SELECT * FROM tasks ORDER BY id"):
                item = dict(row)
                tasks.append({key: item[key] for key in ("id", "title", "kind", "mode", "status", "owner", "epoch")} | {
                    "scopes": json.loads(item["scopes"]), "dependencies": json.loads(item["dependencies"]),
                    "has_checkpoint": item["checkpoint"] != "{}"})
            runs = []
            for row in conn.execute("SELECT * FROM runs ORDER BY id"):
                item = dict(row)
                submitted = [row[0] for row in conn.execute("SELECT agent FROM reports WHERE run=?", (item["id"],))]
                runs.append({"id": item["id"], "integrator": item["integrator"], "closed": bool(item["closed"]),
                             "participants": json.loads(item["participants"]), "submitted": submitted,
                             "has_summary": bool(item["summary"])})
            return {"agents": agents, "tasks": tasks, "runs": runs,
                    "events": [dict(row) for row in conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT 20")]}

    def snapshot(self):
        data = self.status()
        lines = ["# 协作工作台进度", "", "生成：" + utc(), "",
                 "此文件是运行数据库的只读快照；通过 CLI／看板操作，不在此文件认领任务。", "",
                 "| 任务 | 标题 | 状态 | 执行者 | 检查点 |", "| --- | --- | --- | --- | --- |"]
        for item in data["tasks"]:
            clean = lambda x: str(x).replace("|", "/").replace("\n", " ")
            lines.append("| " + " | ".join(clean(x) for x in (
                item["id"], item["title"], item["status"], item["owner"] or "待领取",
                "有" if item["has_checkpoint"] else "无")) + " |")
        lines += ["", "## 参与者", ""]
        for actor in data["agents"]:
            lines.append("- " + actor["id"] + " / " + actor["client"] + " / " +
                         ",".join(actor["roles"]) + " / " + actor["state"])
        lines += ["", "## 调研轮次", ""]
        for run in data["runs"]:
            lines.append("- " + run["id"] + "：提交 " + str(len(run["submitted"])) + "/" +
                         str(len(run["participants"])) + "；汇总者 " + run["integrator"] +
                         "；" + ("已关闭" if run["closed"] else "首稿封存"))
        return "\n".join(lines) + "\n"

    def dispatch(self, task, max_hops=5):
        """监督前台适配器；它退出后才可能接力，不解析供应商聊天文本猜余额。"""
        if type(max_hops) is not int or not 1 <= max_hops <= 20:
            raise ValueError("max_hops 使用 1～20")
        for _ in range(max_hops):
            with self.connection(True) as conn:
                item = self.row(conn, "tasks", task)
                if item["status"] != "todo":
                    raise ValueError("dispatch 只能调度待领取任务")
                choices = json.loads(item["backups"])
                if not choices:
                    raise ValueError("自动执行必须先配置有序 backups，明确授权接力范围")
                selected = None
                for candidate in choices:
                    try:
                        # 事务内尝试失败没有写入，成功立即提交，多个监督者也不会重复派发。
                        selected = self._claim(conn, task, candidate)
                        actor = self.row(conn, "agents", candidate)
                        break
                    except ValueError:
                        continue
                if selected is None:
                    return {"status": "waiting", "reason": "没有可用且职责匹配的接手者"}
            command = json.loads(actor["command"])
            if not command:
                self.message_manual(task, selected["agent"])
                return {"status": "manual", **selected, "context": self.context(task, selected["agent"])}
            context = self.context(task, selected["agent"])
            brief = self.directory / (task + "-" + str(selected["epoch"]) + ".json")
            brief.write_text(dump(context), encoding="utf-8")
            env = dict(os.environ)
            env.update(AGENT_WORKBENCH_ROOT=str(self.root), AGENT_WORKBENCH_BRIEF=str(brief),
                       AGENT_WORKBENCH_TASK=task, AGENT_WORKBENCH_AGENT=selected["agent"],
                       AGENT_WORKBENCH_EPOCH=str(selected["epoch"]))
            result = None
            runner_error = None
            process_started = False
            stderr_path = self.directory / (task + "-" + str(selected["epoch"]) + "-stderr.log")
            try:
                with stderr_path.open("w", encoding="utf-8") as stderr:
                    # shell=False 避免把用户配置的参数重新解释成 shell 命令。
                    with subprocess.Popen(command, cwd=actor["workspace"], env=env, stdout=subprocess.PIPE,
                                          stderr=stderr, text=True, encoding="utf-8") as process:
                        process_started = True
                        for line in process.stdout:
                            self.heartbeat(selected["agent"])
                            try:
                                event = json.loads(line)
                            except ValueError:
                                continue
                            try:
                                if not isinstance(event, dict):
                                    continue
                                if event.get("type") == "checkpoint":
                                    self.checkpoint(task, selected["agent"], selected["epoch"], event["data"])
                                elif event.get("type") == "result":
                                    result = event["data"]
                            except (ValueError, KeyError) as error:
                                # 输出不是事件时忽略；非法结果最后交由 finish 验证。
                                runner_error = str(error)
                        returncode = process.wait()
            except OSError as error:
                self.adapter_stop(task, selected, "adapter_error",
                                  not process_started or bool(actor["foreground"]))
                return {"status": "adapter_error", "error": str(error)}
            if returncode in json.loads(actor["quota_codes"]):
                outcome = self.adapter_stop(task, selected, "quota_exhausted", bool(actor["foreground"]))
                if outcome["status"] != "todo":
                    return outcome
                continue
            if returncode != 0 or result is None or runner_error:
                outcome = self.adapter_stop(task, selected, "adapter_error", bool(actor["foreground"]))
                if outcome["status"] == "superseded":
                    return outcome
                return {"status": "adapter_error", "exit_code": returncode,
                        "error": runner_error or "适配器没有成功提交 result"}
            try:
                if not actor["foreground"]:
                    return self._hold_adapter_result(task, selected, result)
                return self.finish(task, selected["agent"], selected["epoch"], result)
            except ValueError as error:
                outcome = self.adapter_stop(task, selected, "adapter_error", bool(actor["foreground"]))
                if outcome["status"] == "superseded":
                    return outcome
                return {"status": "adapter_error", "error": str(error)}
        return {"status": "waiting", "reason": "达到本轮接力次数上限"}

    def _hold_adapter_result(self, task, claim, result):
        if not isinstance(result, dict) or len(dump(result)) > 64000:
            raise ValueError("result 必须是小型 JSON 对象")
        with self.connection(True) as conn:
            self._owned(conn, task, claim["agent"], claim["epoch"])
            # 成功退出也不证明后台写者已停；保存候选并撤销旧代次，继续占用 scope。
            pending = {"pending_adapter_result": result}
            conn.execute("UPDATE tasks SET status='stopping',epoch=epoch+1,result=? WHERE id=?",
                         (dump(pending), task))
            self.event(conn, "stop", task, "适配器有候选结果，等待人工确认所有写者停止")
        return {"status": "stopping", "reason": "确认实际停写后 takeover，审查 context.pending_result 再 finish"}

    def adapter_stop(self, task, claim, reason, stopped):
        try:
            return self.stop(task, reason, stopped, claim["agent"], claim["epoch"])
        except ValueError:
            # 人已接手或更改代次时，旧适配器错误不得撤销新执行者。
            return {"status": "superseded"}

    def message_manual(self, task, agent):
        with self.connection(True) as conn:
            self.message(conn, "workbench", agent, task,
                         "任务已认领。此客户端尚无启动适配器，请人工读取 context 后开始。")


OPERATIONS = {
    name for name in ("join", "heartbeat", "availability", "create_task", "claim", "context",
                     "checkpoint", "finish", "stop", "takeover", "send", "inbox", "ack",
                     "create_run", "submit_report", "view_run", "close_run", "synthesize", "status")
}


def invoke(workbench, operation, params):
    if operation not in OPERATIONS or not isinstance(params, dict):
        raise ValueError("未知操作或参数不是 JSON 对象")
    return getattr(workbench, operation)(**params)


HTML = """<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent 协作工作台</title>
<style>
body{font:15px system-ui;background:#f3f6fb;color:#233149;max-width:1160px;margin:30px auto;padding:0 24px}
h1{font-size:28px}h2{font-size:20px}section{background:white;padding:20px;border-radius:12px;margin:16px 0}
section>div{overflow-x:auto}table{border-collapse:collapse;width:100%;text-align:left}
td,th{padding:10px;border-bottom:1px solid #e4eaf2;white-space:nowrap}
td:nth-child(2){white-space:normal;min-width:120px}
input,select,button,textarea{font:inherit;padding:9px;border:1px solid #bbc8da;border-radius:6px;margin:4px}
button{background:#e7efff;color:#204475;cursor:pointer}textarea{width:95%;min-height:100px}
pre{white-space:pre-wrap;overflow-wrap:anywhere}small{color:#5d6e86}.alert{color:#9b3520}label{display:inline-block}
</style><h1>Agent 协作工作台</h1>
<p>任务、参与者、接力和反馈在一个地方。人可以参与开发，也可以决定暂停与接手。</p>
<p id="notice" role="status">正在读取…</p>
<section><h2>任务进度</h2><div id="tasks"></div></section>
<section><h2>参与者登记</h2><div id="agents"></div>
<small>最近活动时间用于判断是否需要核查；时间过期不会自动接管。</small></section>
<section><h2>独立调研</h2><div id="runs"></div><small>此处只显示提交数量，首稿正文不自动进入公共进度。</small></section>
<section><h2>我的任务与反馈</h2><label>参与者 <select id="viewer"></select></label>
<button id="read">读取收件箱</button><pre id="inbox"></pre>
<label>任务 ID <input id="context-task"></label><button id="context-read">读取已领取任务</button>
<pre id="context"></pre></section>
<section><h2>人工操作</h2><p>点击“暂停”先保留占用；确认原执行者停止后再接手。</p>
<label>任务 ID <input id="task"></label><label>接手者 ID <input id="next" value="human"></label>
<label><input id="stopped" type="checkbox">已确认原执行者停止写入</label>
<button id="pause">暂停任务</button><button id="takeover">接手任务</button><br>
<label>调研轮次 <input id="run"></label>
<label><input id="missing" type="checkbox">允许人工截止，保留未交付名单</label>
<button id="close">关闭轮次</button><pre id="action"></pre></section>
<section><h2>创建工作</h2>
<label>任务编号 <input id="new-id" placeholder="AUTH001"></label>
<label>标题 <input id="new-title" placeholder="实现登录模块"></label>
<label>职责 <select id="new-kind"><option value="development">开发</option><option value="test">独立测试</option>
<option value="research">协作调研</option><option value="integration">整合</option></select></label><br>
<label>可修改目录 <input id="new-scopes" placeholder="src/auth, docs/auth"></label>
<label>测试哪个开发任务 <input id="new-subject" placeholder="测试时填写"></label><br>
<label>依赖任务 <input id="new-deps" placeholder="可留空，逗号分隔"></label>
<label>备用执行者顺序 <input id="new-backups" placeholder="codex-1, wb-1, human"></label>
<p>目标、公共接口与验收要求</p><textarea id="new-contract"></textarea><button id="create">创建任务</button></section>
<section><h2>给协作者留言</h2>
<label>发送者 <input id="from" value="human"></label><label>收件人 <input id="to"></label>
<label>关联任务 <input id="message-task"></label>
<textarea id="message-body" placeholder="具体结果、复现步骤或需要对方处理的问题"></textarea>
<button id="send-message">发送反馈</button></section>
<section><details><summary>高级客户端接口：登记、提交与调研操作</summary>
<label>操作 <select id="operation"><option>create_task</option><option>send</option>
<option>checkpoint</option><option>finish</option><option>create_run</option>
<option>submit_report</option><option>synthesize</option><option>join</option></select></label>
<p><small>填写与 CLI 相同的 JSON 参数；说明文件附有可复制示例。</small></p>
<textarea id="params" spellcheck="false">{}</textarea><button id="execute">执行</button></details></section>
<section><h2>近期事件</h2><pre id="events"></pre></section>
<script>
const $=id=>document.getElementById(id),token=location.hash.slice(1);
const labels={development:'开发',test:'独立测试',research:'调研',integration:'整合',developer:'开发者',
 tester:'测试者',researcher:'研究者',integrator:'汇总者',human:'人',todo:'待领取',active:'工作中',
 awaiting_review:'等待独立验收',done:'已完成',stopping:'等待确认停写',available:'可领取',
 paused:'暂停',quota_exhausted:'额度耗尽',manual:'人工启动',command:'适配器启动'};
const label=x=>labels[x]||x, list=id=>$(id).value.split(',').map(x=>x.trim()).filter(Boolean);
async function call(operation,params={}){
 const response=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json','X-Workbench-Token':token},
 body:JSON.stringify({operation,params})});
 const value=await response.json();if(!response.ok)throw Error(value.error);return value;
}
function table(id,headers,rows){
 const t=document.createElement('table'),head=t.createTHead().insertRow();
 headers.forEach(x=>{const c=document.createElement('th');c.textContent=x;head.append(c)});
 rows.forEach(row=>{const r=t.insertRow();row.forEach(x=>{const c=r.insertCell();c.textContent=String(x??'—')})});
 $(id).replaceChildren(t);
}
async function refresh(){
 try{const data=await call('status');
 table('tasks',['任务','标题','职责','状态','执行者','修改范围','检查点'],
 data.tasks.map(x=>[x.id,x.title,label(x.kind),label(x.status),x.owner,x.scopes.join(', ')||'只读',x.has_checkpoint?'有':'无']));
 table('agents',['ID','客户端','职责','可用性','最近活动','启动方式'],
 data.agents.map(x=>[x.id,x.client,x.roles.map(label).join(', '),
 data.tasks.some(t=>t.owner===x.id)?'工作中':label(x.state),x.last_seen_seconds+' 秒前',label(x.transport)]));
 table('runs',['轮次','指定汇总者','已提交','状态'],
 data.runs.map(x=>[x.id,x.integrator,x.submitted.length+'/'+x.participants.length,x.closed?'已关闭':'首稿封存']));
 const selected=$('viewer').value;
 $('viewer').replaceChildren(...data.agents.map(x=>{const o=document.createElement('option');o.value=x.id;o.textContent=x.id;return o}));
 if(data.agents.some(x=>x.id===selected))$('viewer').value=selected;
 $('events').textContent=data.events.map(x=>new Date(x.created).toLocaleString()+' · '+x.kind+' · '+x.item+' · '+x.detail).join('\\n');
 $('notice').textContent='最近更新 '+new Date().toLocaleTimeString();
 }catch(e){$('notice').textContent=e.message}
}
async function action(operation,params,target='action'){
 try{$(target).textContent=JSON.stringify(await call(operation,params),null,2);await refresh()}
 catch(e){$(target).textContent=e.message}
}
$('read').onclick=()=>action('inbox',{agent:$('viewer').value},'inbox');
$('context-read').onclick=()=>action('context',{task:$('context-task').value,agent:$('viewer').value},'context');
$('pause').onclick=()=>action('stop',{task:$('task').value,reason:'paused',stopped:false});
$('takeover').onclick=()=>action('takeover',{task:$('task').value,agent:$('next').value,stopped:$('stopped').checked});
$('close').onclick=()=>action('close_run',{run:$('run').value,actor:'human',allow_missing:$('missing').checked});
$('create').onclick=()=>{
 const params={task:$('new-id').value,title:$('new-title').value,kind:$('new-kind').value,
 scopes:list('new-scopes'),contract:$('new-contract').value,dependencies:list('new-deps'),backups:list('new-backups')};
 if(params.kind==='test')params.subject=$('new-subject').value;
 action('create_task',params);
};
$('send-message').onclick=()=>action('send',{sender:$('from').value,recipient:$('to').value,
 task:$('message-task').value,body:$('message-body').value});
$('execute').onclick=()=>{try{action($('operation').value,JSON.parse($('params').value))}catch(e){$('action').textContent=e.message}};
refresh();setInterval(refresh,5000);
</script></html>"""


def make_server(workbench, port=0):
    token = secrets.token_urlsafe(32)
    with workbench.connection(True) as conn:
        # 本地人工界面有明确的人类入口；保留已存在的同名登记，不改其角色。
        cursor = conn.execute("INSERT OR IGNORE INTO agents VALUES(?,?,?,?,?,?,?,?,?)",
                              ("human", "本机操作者", dump(["human", "integrator"]), "available",
                               "[]", "[]", str(workbench.root), 0, time.time()))
        if cursor.rowcount:
            workbench.event(conn, "join", "human", "人工界面入口")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, value, html=False):
            data = value.encode("utf-8") if html else dump(value).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8" if html else "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if urlparse(self.path).path != "/":
                return self.reply(404, {"error": "未找到"})
            self.reply(200, HTML, True)

        def do_POST(self):
            if self.path != "/api":
                return self.reply(404, {"error": "未找到"})
            received = self.headers.get("X-Workbench-Token", "")
            if not secrets.compare_digest(received.encode(), token.encode()):
                return self.reply(403, {"error": "请使用终端显示的完整本地 URL"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 200000:
                    raise ValueError("请求大小不合法")
                request = json.loads(self.rfile.read(length))
                if not isinstance(request, dict):
                    raise ValueError("请求必须为对象")
                result = invoke(workbench, request["operation"], request.get("params", {}))
                self.reply(200, result)
            except (ValueError, TypeError, KeyError, sqlite3.Error) as error:
                self.reply(400, {"error": str(error)})

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    return server, "http://127.0.0.1:" + str(server.server_port) + "/#" + token


def demo(workbench):
    if workbench.db.exists():
        raise ValueError("演示必须使用新的演示目录，不覆盖真实运行状态")
    for agent, client, roles in (
            ("human", "人", ["human", "integrator"]),
            ("codex-1", "Codex（演示）", ["developer"]),
            ("wb-1", "WB（演示）", ["developer", "researcher"]),
            ("dsh-1", "DSH（演示）", ["tester", "researcher"]),
            ("zcode-1", "ZCode（演示）", ["researcher"]),
            ("wb-2", "WB 第二实例（演示）", ["researcher", "integrator"])):
        workbench.join(agent, client, roles)
    workbench.create_task("D001", "实现登录模块", "development", ["src/login"],
                          "登录契约：错误凭据返回明确错误。", backups=["codex-1", "wb-1", "human"])
    claim = workbench.claim("D001", "codex-1")
    workbench.checkpoint("D001", "codex-1", claim["epoch"],
                         {"completed": "已完成请求校验", "remaining": "补充错误处理", "revision": "demo-baseline"})
    workbench.create_task("D002", "实现进度展示", "development", ["src/progress"],
                          "进度仅展示公共状态。")
    workbench.claim("D002", "wb-1")
    workbench.create_task("T001", "独立验收登录模块", "test", ["tests/login"],
                          "独立设计边界用例；测试计划仅向此任务领取者提供。", subject="D001")
    workbench.create_run("R001", "哪种任务协调机制适合本地多客户端？",
                         "同一问题；优先一手来源，区分事实与推断，提交后关闭轮次再汇总。",
                         ["wb-1", "dsh-1", "zcode-1"], "wb-2")
    workbench.submit_report("R001", "dsh-1", {"claims": [
        {"kind": "proposal", "statement": "演示候选已封存，不展示正文。", "sources": []}]})
    return workbench.status()


def main():
    # Windows 重定向 stderr 可能沿用本机代码页；CLI 协议统一 UTF-8。
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    call = commands.add_parser("call")
    call.add_argument("operation", choices=sorted(OPERATIONS))
    source = call.add_mutually_exclusive_group()
    source.add_argument("--data", default=None, help="JSON 参数")
    source.add_argument("--file", help="UTF-8 JSON 参数文件")
    commands.add_parser("status")
    commands.add_parser("snapshot")
    commands.add_parser("demo")
    serve = commands.add_parser("serve")
    serve.add_argument("--port", type=int, default=0)
    dispatch = commands.add_parser("dispatch")
    dispatch.add_argument("--task", required=True)
    dispatch.add_argument("--max-hops", type=int, default=5)
    args = parser.parse_args()
    try:
        workbench = Workbench(args.root)
        if args.command == "serve":
            server, address = make_server(workbench, args.port)
            print(address, flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
            return
        if args.command == "snapshot":
            print(workbench.snapshot())
            return
        if args.command == "call":
            params = json.loads(Path(args.file).read_text(encoding="utf-8-sig") if args.file else args.data or "{}")
            value = invoke(workbench, args.operation, params)
        elif args.command == "demo":
            value = demo(workbench)
        elif args.command == "dispatch":
            value = workbench.dispatch(args.task, args.max_hops)
        else:
            value = workbench.status()
        print(json.dumps(value, ensure_ascii=False, indent=2))
    except (ValueError, TypeError, KeyError, OSError, sqlite3.Error) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    main()

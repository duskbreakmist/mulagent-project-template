"""只读检查模板完整性；v2 另检查 Markdown 本地链接和任务 status，不初始化或修复工程。"""
import argparse
import ast
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

TASK_STATUSES = {"todo", "in_progress", "blocked", "review", "done"}
# 固定最小协议／工具锚点，而不是复制整个33项清单；允许新增组成文件。
CORE_FILES = {"AGENTS.md", ".agents/PROTOCOL.md", ".agents/coordination.md",
              ".agents/guides/git.md", ".agents/guides/modes.md",
              ".agents/tasks/TEMPLATE-lite.md", ".agents/template_manifest.json",
              "tools/check_template.py", "tools/template_manager.py"}
DEVELOPMENT_PREFIXES = ("docs/maintenance/", "tests/", ".github/", "tools/legacy/")


def safe_path(root, relative):
    # 解析符号链接后再核对边界，清单、链接和任务扫描都不能越出工程。
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError("路径逃逸工程: " + str(relative))
    return path


def readable_text(path):
    text = path.read_text(encoding="utf-8")
    if not text.strip() or text.startswith("\ufeff") or "\ufffd" in text:
        raise ValueError("空文件或编码异常: " + str(path))
    return text


def prose_only(text):
    # 示例代码不参与链接校验；支持反引号和波浪线围栏，长度必须匹配。
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
            continue
        if match:
            fence = match[1]
            continue
        lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines))


def destination(text, start):
    """读取链接首个目标，允许尖括号、转义和括号文件名；标题不属于目标。"""
    while start < len(text) and text[start].isspace():
        start += 1
    if start < len(text) and text[start] == "<":
        end = text.find(">", start + 1)
        return text[start + 1:end] if end >= 0 else ""
    result = []
    depth = 0
    while start < len(text):
        char = text[start]
        if char == "\\" and start + 1 < len(text):
            result.append(text[start + 1])
            start += 2
            continue
        if char.isspace() or (char == ")" and depth == 0):
            break
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        result.append(char)
        start += 1
    return "".join(result)


def check_links(root, path, text):
    prose = prose_only(text)
    targets = [destination(prose, match.end()) for match in re.finditer(r"\]\(", prose)]
    # 引用式链接的目标在定义中；不把脚注定义当文件路径。
    targets += [destination(prose, match.end()) for match in
                re.finditer(r"(?m)^ {0,3}\[(?!\^)[^\]\n]+\]:\s*", prose)]
    for target in targets:
        if not target or target.startswith("#"):
            continue
        parts = urlsplit(target)
        if parts.scheme or parts.netloc:
            continue  # 不联网验证外部 URL／mailto／Codex 链接。
        local = unquote(parts.path)
        if not local:
            continue
        relative = (path.parent / local).relative_to(root) if not Path(local).is_absolute() else Path(local)
        resolved = safe_path(root, relative)
        if not resolved.exists():
            raise ValueError("断链: " + str(path.relative_to(root)) + " -> " + target)


def check_task_statuses(root, directory=".agents/tasks"):
    tasks = safe_path(root, directory)
    for path in tasks.rglob("*.md"):
        safe_path(root, path.relative_to(root))
        if path.name == "README.md" or path.name.startswith("TEMPLATE"):
            continue
        text = readable_text(path).split("\n## ", 1)[0]
        # 只读取任务头部字段；正文示例或检查输出中的 status 不是任务状态。
        statuses = re.findall(r"(?m)^\s*(?:-\s*)?status\s*:\s*([^\n]*)$", text)
        if len(statuses) > 1:
            raise ValueError("重复 status: " + str(path.relative_to(root)))
        if statuses and statuses[0].split("#", 1)[0].strip().strip("`") not in TASK_STATUSES:
            raise ValueError("非法任务 status: " + str(path.relative_to(root)))


def validate(root, maintenance=False):
    root = Path(root).resolve()
    manifest_path = safe_path(root, ".agents/template_manifest.json")
    manifest = json.loads(readable_text(manifest_path))
    version = manifest.get("version")
    if manifest.get("format") != "project_templateA" or type(version) is not int or version not in (1, 2):
        raise ValueError("不支持的模板格式或版本")
    required = manifest.get("required")
    if not isinstance(required, list) or not required:
        raise ValueError("模板清单缺失")
    if version == 2 and not CORE_FILES.issubset(name for name in required if isinstance(name, str)):
        raise ValueError("清单缺少核心协议／工具: " + ", ".join(sorted(CORE_FILES - set(
            name for name in required if isinstance(name, str)))))
    seen = set()
    markdown = []
    for name in required:
        if not isinstance(name, str):
            raise ValueError("清单项必须是相对路径字符串")
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or name in seen:
            raise ValueError("非法或重复路径: " + name)
        seen.add(name)
        if name.startswith(DEVELOPMENT_PREFIXES):
            raise ValueError("开发资产不属于业务分发清单: " + name)
        path = safe_path(root, relative)
        if not path.is_file():
            raise ValueError("缺少文件: " + name)
        text = readable_text(path)
        if version == 2 and path.suffix == ".py":
            ast.parse(text, filename=name)  # 只校验语法，绝不执行待检查代码。
        if path.suffix.lower() == ".md":
            markdown.append((path, text))
    if version == 2:
        for path, text in markdown:
            check_links(root, path, text)
        check_task_statuses(root)
    if maintenance:
        # 显式维护模式，避免把业务项目同名目录或历史快照当成活跃任务板。
        for name in ("README.md", "CURRENT.md", "COORDINATION.md"):
            path = safe_path(root, "docs/maintenance/" + name)
            check_links(root, path, readable_text(path))
        for directory in ("tasks", "runs", "history"):
            for path in safe_path(root, "docs/maintenance/" + directory).rglob("*.md"):
                safe_path(root, path.relative_to(root))
                check_links(root, path, readable_text(path))
        check_task_statuses(root, "docs/maintenance/tasks")
    return len(required)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--maintenance", action="store_true", help="另检查母模板维护入口、记录链接和任务状态")
    args = parser.parse_args()
    try:
        count = validate(args.root, args.maintenance)
    except (OSError, ValueError, SyntaxError) as error:
        parser.exit(1, str(error) + "\n")
    print("TEMPLATE_OK files=" + str(count))


if __name__ == "__main__":
    main()

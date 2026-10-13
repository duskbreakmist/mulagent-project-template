# DOC005-CODEX 分离母模板与业务README

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户2026-10-13授权实施README分离并同步相关引用，单人串行维护
- owner: codex-bootstrap-integrator-20261011
- created: 2026-10-13
- updated: 2026-10-13
- base_commit: a6d12bd84668e199532c7cd9f397f391ef466a35
- version_tag: 无

## Objective

母README不进入新业务工程，模板使用须知独立分发；业务README正常由业务Git记录，独立于模板升级基线，已有文件与旧版本兼容保留。

## Scope

根README、template_readme、docs/template-usage、AGENTS、两种task格式、manifest、管理器与检查器、对应测试；维护入口、本task及CURRENT／必要摘要归档。历史任务／版本说明／原始归档保持当时语境，不机械替换其他目录的README文件名。

## Completed

新清单移除母README（35→34），init另生成精简业务README并随BOOTSTRAP提交，但不写入模板文件基线；旧清单按原版本安装。update从新基线移除旧README记录，不删文件、不创建缺失业务README或报告为模板删除。
template_readme保留文件名并改为模板使用须知，集中工程约定说明；相关活动引用区分母／模板／业务文档。业务README存在时检查器仍只读检查编码与本地链接，缺失不算漏分发。

## Verification

93项完整回归通过（243.397秒，退出0，.test-tmp/DOC005-full-tests.log）；补充元数据用例单独通过（8.687秒）。最终增加旧清单回选保护后，两个legacy_readme定向用例通过（26.124秒）；最终源码共94项；[Windows／Ubuntu完整CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38364780433)均成功。
新工程README正常由BOOTSTRAP提交、不会出现在模板基线；母README独立变化不影响业务文件；旧清单升级保留业务定制、实际删除及回选旧清单不恢复README；仅元数据迁移预览只读。34项维护结构／编码／链接与diff检查通过。

实际Git快照CLI演练：以v0.2.0安装旧工程，改业务README并保存，再用其自带旧CLI切到本次main提交；内容不变、旧基线项如预期暂留。提交后用已更新CLI预览／实际清理（0文件变更），基线项移除且业务内容保留；最终34项检查与独立Git干净。新版空工程init --commit生成精简README，Git确认跟踪且模板基线不含它，34项检查通过。
实现提交b629ecf2715c27a1ef422e8c12be45cc9f0bdc76通过官方API原样推送，逐项核对32个Git对象且非强制更新；包含此前用户授权的PILOT001文档提交并保留其作者与历史。已核对远端main与本地提交一致，不移动任何发布标签。

## Remaining

本次目标完成，收尾仅保存维护记录。新版行为在main提交生效；已发布v0.2.0标签及已有业务工程未改，不自动升级它们或生成新release。实际网络Git clone仍未复验，本地版本演练使用与公开标签一致的Git快照。

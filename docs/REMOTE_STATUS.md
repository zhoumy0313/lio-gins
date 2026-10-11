# 项目远程与推送记录

2026-10-12，用户明确授权推送到 `git@github.com:zhoumy0313/lio-gins.git`。项目origin指向该地址；`research/lio-gins-r1`设为upstream。目标原为空仓库，首次推送exit0，并以ls-remote核对本地HEAD、远端HEAD及分支SHA一致：f06a3ed102a60a15f2bc6f78a629eae5f6c04b7d。远端默认分支为research/lio-gins-r1。

该事实记录于artifacts/remote_push/initial_checkpoint_push.json；后续仅记录本次授权和推送范围的归档提交单独推送、核验，避免SHA自引用。未force push或修改旧VPR remote。

仅推送Git跟踪的源码、配置、文档、轻量证据、论文草稿版本及提交历史。原始bag/文本、完整outputs、cache、build、venv、第三方源码和受版权参考文档均未纳入。轻量数值证据已有远端副本；完整实验数值输出与raw备份仍false，不能把代码推送称完整备份。

首次SSH主机校验失败后，核对GitHub官方Ed25519指纹，使用项目cache/push_github/known_hosts及单命令GIT_SSH_COMMAND重试；没有修改~/.ssh、全局Git/网络配置、创建凭据或更改账号。本机后续SSH操作如仍有主机校验问题，需使用相同项目内记录或用户自己的已验证SSH设置。

旧阶段报告和封存审计中的“无remote”是当时事实，保留原样。本文件及GOAL_STATE记录后续授权后的当前状态。科研结论仍NO_ADDITIONAL_GAIN，不因推送改变。

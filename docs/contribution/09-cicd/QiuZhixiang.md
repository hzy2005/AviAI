# CI/CD 配置贡献说明

姓名：邱志翔  学号：待补充  角色：前端  日期：2026-04-30

## 完成的工作

### 工作流相关
- [x] 参与编写 / 审查 `.github/workflows/ci.yml`
- [x] 配置 Codecov 覆盖率上传（backend / frontend flag）
- [x] 添加 README 状态徽章

### 代码适配
- [x] 本地测试命令与 CI 一致，无需额外配置
- [x] 代码通过 Lint 检查（ESLint）
- [x] 前端覆盖率报告生成 `frontend/coverage/lcov.info`

### 可选项
- [x] 配置 Dependabot 自动更新依赖
- [ ] 集成 CodeRabbit AI 代码审查
- [ ] 使用 act 本地验证工作流

## PR 链接
- PR #40: https://github.com/hzy2005/AviAI/pull/40

## CI 运行链接
- 待 workflow 合并并首次成功运行后补充

## 遇到的问题和解决
1. 问题：原有前端测试命令依赖 PowerShell 脚本，不适合直接放到 Ubuntu CI。解决：改为 Node 脚本入口，统一本地和 CI 的测试行为。
2. 问题：仓库里原先是拆分工作流，且前端 coverage 里包含占位上传逻辑。解决：合并为单个 `ci.yml`，保留真实测试产物上传。
3. 问题：README 徽章仍指向旧分支和旧工作流。解决：统一切换为 `main` 分支和 `ci.yml` 工作流地址。
4. 问题：前端依赖后续升级如果完全手动维护，容易遗漏。解决：新增 `.github/dependabot.yml`，让 GitHub 定期检查 `frontend/` 下的 npm 依赖更新。

## 心得体会

这次主要收获是把“本地能跑”进一步整理成“CI 也能稳定跑”。前端测试命令如果不够明确，很容易在不同系统下表现不一致；把测试入口、覆盖率产物和工作流路径统一之后，后续联调和验收会顺畅很多。

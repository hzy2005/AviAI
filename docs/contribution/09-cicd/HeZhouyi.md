# CI/CD 配置贡献说明

姓名：何周屹  学号：2312190419  角色：后端  日期：2026-05-05

## 完成的工作

### 工作流相关
- [x] 参与编写 / 审查 `.github/workflows/ci.yml`
- [x] 配置 Codecov 覆盖率上传（backend flag）
- [x] 添加 README 状态徽章（CI 徽章补充 `?branch=main` 参数，确保只反映主分支状态）

### 代码适配
- [x] 本地测试命令与 CI 一致，无需额外配置
- [x] 代码通过 Lint 检查（ruff 零警告）
- [x] 后端覆盖率达标：74 个用例全部通过，总覆盖率 84%（> 60% 要求）

### 可选项
- [x] 配置 Dependabot 自动更新依赖（补全后端 pip ecosystem）
- [x] 集成 CodeRabbit AI 代码审查（新增 `.coderabbit.yaml`，设置中文审查）
- [x] 添加构建矩阵（Python 3.11 / 3.12 并行运行后端测试）
- [x] 使用 act 本地验证工作流

## 具体变更说明

### 1. 补全 Dependabot 后端配置

`.github/dependabot.yml` 原仅监控前端 npm 依赖，缺少后端配置。新增 `pip` ecosystem 监控 `/backend` 目录，每周自动扫描 `requirements.txt` 并开 PR，打上 `dependencies` / `backend` 标签。

### 2. 添加 Python 多版本构建矩阵

`.github/workflows/ci.yml` 后端 job 新增 `strategy.matrix`，覆盖 Python 3.11（本地 conda 开发环境）和 3.12（CI 原有版本），两个版本并行运行，确保跨版本兼容性。

### 3. 集成 CodeRabbit AI 代码审查

新增 `.coderabbit.yaml` 配置文件，设置审查语言为中文（zh-CN），使用 `chill` 风格，排除 `docs/`、markdown 文件和覆盖率报告目录，聚焦真实代码变更。已在 coderabbit.ai 完成 GitHub 仓库授权，后续每个 PR 将自动收到 AI 审查评论。

### 4. 优化 README 状态徽章

- CI 徽章补充 `?branch=main`，只反映主分支构建状态，feature 分支失败不影响徽章展示
- 新增 CodeRabbit 审查状态徽章

## PR 链接

- PR 链接：待提交后填写

## CI 运行链接

- https://github.com/hzy2005/AviAI/actions/runs/25368017066

## 遇到的问题和解决

1. 问题：Dependabot 原配置只有前端 npm，后端 `requirements.txt` 无法自动更新。  
   解决：在 `dependabot.yml` 追加 `pip` ecosystem 配置，与前端保持一致的标签和 commit 前缀风格。

2. 问题：CI 后端 job 原本只跑 Python 3.12，无法发现跨版本兼容性问题。  
   解决：添加 `strategy.matrix`，同时覆盖 3.11 和 3.12，两个版本并行跑 `ruff check` 和 `pytest`，已本地验证 74 个用例在两个版本均可通过。

3. 问题：CodeRabbit 默认英文审查，不便于团队阅读。  
   解决：在 `.coderabbit.yaml` 中设置 `language: zh-CN`，并排除文档目录，减少无效审查噪音。

## 心得体会

这次 CI/CD 配置让我更清晰地理解了"本地能跑"和"CI 稳定跑"之间的差距。通过矩阵构建发现了项目需要同时兼容 Python 3.11（开发环境）和 3.12（CI 环境）这一潜在问题，并及早在流水线层面加以验证。Dependabot 和 CodeRabbit 的引入则把依赖管理和代码审查从手动操作变成了自动化流程，降低了长期维护成本。

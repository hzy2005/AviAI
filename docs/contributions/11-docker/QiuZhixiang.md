# Docker 部署贡献说明

姓名：邱志翔  
学号：312190432  
日期：2026-05-19

## 我完成的工作

### 1. Dockerfile 编写

- [ ] 前端 Dockerfile（多阶段构建）
- [ ] 后端 Dockerfile（多阶段构建）
- [ ] `.dockerignore` 文件
- [x] 复核现有 Dockerfile、`.dockerignore` 和健康检查配置是否满足作业清单

### 2. Compose 配置

- [ ] 开发环境 `compose.yaml`
- [ ] 生产环境 `compose.prod.yaml`
- [ ] 健康检查配置
- [x] 复核开发和生产 Compose 配置能通过 `docker compose config` 解析
- [x] 补充根目录 `.env.example`，说明 Docker Compose 需要的环境变量和生产 secrets 文件

### 3. 自动化部署

- 选择了选项 A：GitHub Actions 构建并推送镜像到 GHCR
- 具体内容：
  - 复核 `.github/workflows/docker.yml` 中的前后端镜像构建配置
  - 复核 GHCR 推送配置
  - 复核 Trivy 镜像漏洞扫描配置

## PR 链接

- PR ：https://github.com/hzy2005/AviAI/pull/75

## 遇到的问题和解决

1. 问题：仓库中已有 `backend/.env.example`，但作业提交清单要求根目录提供 `.env.example`。  
   解决：补充根目录 `.env.example`，列出 `DEEPSEEK_API_KEY`、`GITHUB_REPOSITORY`、`VERSION` 等 Compose 相关变量，并说明生产 secrets 文件需要本地创建，不能提交真实密钥。

2. 问题：`docs/contributions/11-docker/` 目录缺失，无法满足个人贡献说明提交要求。  
   解决：新增 `docs/contributions/11-docker/`，并按作业模板补充何周屹和邱志翔的 Docker 部署贡献说明。

3. 问题：生产环境使用 Docker secrets，仓库中不会提交真实 `secrets/*.txt`，验收运行前容易遗漏。  
   解决：在 `.env.example` 和贡献说明中明确列出需要本地创建的 `secrets/db_password.txt`、`secrets/db_root_password.txt`、`secrets/backend_secret_key.txt`。

4. 问题：生产 compose 使用 GHCR 镜像，适合 CI 构建推送后的部署；如果本地没有同名镜像，直接运行生产 compose 可能拉取失败。  
   解决：在复核记录中说明该风险，验收时优先使用开发环境 `docker compose up -d` 截图，生产环境需先完成 GHCR 镜像构建或手动准备同名镜像。

## AI 使用情况

- 使用了哪些 Prompt：
  - 请检查项目 Docker 作业还缺什么，不要修改代码。
  - 请补齐缺失的 Docker 作业材料，不修改原有代码。
- AI 帮助解决了哪些问题：
  - 对照作业清单检查 Dockerfile、Compose、GitHub Actions、`.env.example` 和个人贡献说明。
  - 识别缺失的 `docs/contributions/11-docker/` 目录和根目录 `.env.example`。
  - 整理 Docker 作业验收时需要注意的 secrets 和 GHCR 镜像风险。

## 心得体会

这次补充工作让我意识到 Docker 作业不只是写出能运行的配置，还要把验收材料和运行前准备交代清楚。真实项目里，密钥文件不能提交到仓库，但文档和模板必须告诉使用者要准备什么；CI 已经能构建镜像，也要说明生产 compose 依赖 GHCR 镜像。把这些细节补齐后，后续截图、提交和老师验收都会更顺畅。

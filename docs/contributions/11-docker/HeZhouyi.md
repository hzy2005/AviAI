# Docker 部署贡献说明

姓名：何周屹
学号：2312190419
日期：2026-05-12

## 我完成的工作

本次 Docker 容器化部署中，我主要负责前后端容器化实现、Docker Compose 编排、生产环境配置和 GitHub Actions 自动化镜像构建扫描。

### 1. Dockerfile 编写

- [x] 前端 Dockerfile（多阶段构建）
- [x] 后端 Dockerfile（多阶段构建）
- [x] `.dockerignore` 文件

具体内容：

- 新增 `frontend/Dockerfile`，使用 Node 阶段安装依赖、执行质量检查，并使用 Nginx runtime 镜像提供前端说明页。
- 新增 `backend/Dockerfile`，使用 Python 3.11 slim 镜像和多阶段构建安装后端依赖。
- 后端运行时使用非 root 用户 `appuser`，降低容器运行权限风险。
- 后端容器暴露 8000 端口，并配置 `/health` 健康检查。
- 新增 `frontend/.dockerignore` 和 `backend/.dockerignore`，排除 `.env`、`.git`、`node_modules`、缓存、覆盖率产物、构建产物和日志文件。
- 新增 `backend/requirements.docker.txt`，为 Docker 镜像构建提供更精简的依赖集合。

### 2. Compose 配置

- [x] 开发环境 `compose.yaml`
- [x] 生产环境 `compose.prod.yaml`
- [x] 健康检查配置
- [x] 数据持久化配置
- [x] 生产环境 secrets 配置

具体内容：

- 新增 `compose.yaml`，编排 `frontend`、`backend`、`db`、`redis` 服务。
- 后端服务启动时执行 `alembic upgrade head`，再启动 Uvicorn。
- MySQL 使用 `mysql:8.4`，配置 `utf8mb4` 字符集和健康检查。
- Redis 使用 `redis:7-alpine`，并配置数据卷。
- 上传目录、MySQL 数据和 Redis 数据均使用 Docker volume 持久化。
- 新增 `compose.prod.yaml`，使用 GHCR 镜像、`restart: unless-stopped`、资源限制和 Docker secrets。
- 生产环境数据库密码、root 密码和后端 `SECRET_KEY` 均通过 `secrets/` 目录读取，避免直接写入配置文件。
- 新增 `secrets/.gitignore`，防止真实密钥文件进入仓库。

### 3. 自动化部署

选择了选项 A：构建并推送镜像到 GHCR。

具体内容：

- 新增 `.github/workflows/docker.yml`。
- 使用矩阵分别构建 `backend` 和 `frontend` 镜像。
- 推送分支和手动触发时登录 GHCR 并推送镜像。
- Pull Request 场景只构建本地镜像，不推送到仓库。
- 使用 Docker Buildx 和 GitHub Actions cache 加速构建。
- 使用 `docker/metadata-action` 生成分支、PR、commit sha 和 latest 标签。
- 集成 Trivy 扫描镜像漏洞，阻断 CRITICAL/HIGH 级别风险。

### 4. 镜像安全和漏洞修复

- [x] 减少后端镜像中的漏洞扫描面
- [x] 升级前端 runtime 镜像包
- [x] 调整 Dockerfile 中的系统包升级和清理逻辑

具体内容：

- 在后端镜像中清理 `setuptools`、`wheel`、`pkg_resources` 等非运行时必要组件，减少漏洞扫描噪声。
- 在前端 Nginx runtime 镜像中执行 Alpine 包升级，修复基础镜像中的已知漏洞。
- 保持前后端容器使用非 root 用户运行。

## PR 链接

- PR #74: https://github.com/hzy2005/AviAI/pull/74

## 遇到的问题和解决

1. 问题：项目同时包含微信小程序前端和 FastAPI 后端，二者运行方式不同，不能使用单一 Dockerfile 覆盖全部场景。

   解决：分别为 `frontend` 和 `backend` 编写 Dockerfile，并在 Compose 中作为独立服务编排。

2. 问题：后端依赖中包含较重的机器学习依赖，如果全部安装会增大镜像体积。

   解决：新增 `backend/requirements.docker.txt`，Docker 部署场景只安装后端运行所需依赖，降低镜像体积和构建时间。

3. 问题：后端启动依赖数据库，如果数据库尚未就绪会导致迁移或服务启动失败。

   解决：在 Compose 中为 MySQL 配置健康检查，并让后端通过 `depends_on` 等待数据库 healthy 后再启动。

4. 问题：生产环境不能把数据库密码、root 密码和后端密钥硬编码到 Compose 文件中。

   解决：在 `compose.prod.yaml` 中使用 Docker secrets，并通过 `secrets/.gitignore` 避免真实密钥文件提交到仓库。

5. 问题：镜像扫描发现基础镜像或构建工具链中存在 HIGH/CRITICAL 级别风险。

   解决：升级前端 runtime 包，清理后端镜像中不必要的构建工具和包元数据，并在 GitHub Actions 中保留 Trivy 扫描作为持续检查。

## AI 使用情况

- 使用 AI 辅助整理 Dockerfile 多阶段构建方案，确认非 root 用户、健康检查、端口暴露和依赖安装方式。
- 使用 AI 辅助设计 Compose 服务依赖、健康检查、数据卷和 secrets 管理结构。
- 使用 AI 辅助分析 Trivy 扫描结果，定位可通过镜像清理或基础包升级解决的问题。

## 心得体会

这次 Docker 容器化部署让我更清楚地理解了开发环境和生产环境之间的差异。开发环境更强调快速启动和本地调试，生产环境则需要关注镜像来源、运行权限、密钥管理、服务健康检查和资源限制。通过前后端 Dockerfile、Compose 编排和 GitHub Actions 镜像构建扫描的组合，项目可以从“本地能跑”进一步提升到“可重复构建、可自动检查、可部署运行”的状态。

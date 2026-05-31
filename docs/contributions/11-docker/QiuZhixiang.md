# Docker 部署贡献说明

姓名：邱志翔
学号：2312190432
日期：2026-05-12

## 我完成的工作

本次 Docker 容器化部署中，我主要负责代码检查、配置复核和贡献文档补充。前后端 Dockerfile、Compose 配置和 GitHub Actions 自动化构建扫描主要由何周屹完成。

### 1. Dockerfile 编写

- [ ] 前端 Dockerfile（多阶段构建）
- [ ] 后端 Dockerfile（多阶段构建）
- [ ] `.dockerignore` 文件
- [x] 检查前后端 Dockerfile 是否满足作业要求
- [x] 检查 `.dockerignore` 是否排除了 `.env`、`.git`、`node_modules`、测试覆盖率产物等无关文件

检查内容：

- 确认 `frontend/Dockerfile` 使用多阶段构建，并通过 Nginx 运行前端说明页。
- 确认 `backend/Dockerfile` 使用 Python slim 镜像、多阶段构建和非 root 用户运行。
- 确认后端容器暴露 8000 端口，并配置健康检查。
- 确认前后端 `.dockerignore` 避免把本地依赖、缓存、密钥文件和构建产物打入镜像。

### 2. Compose 配置

- [ ] 开发环境 `compose.yaml`
- [ ] 生产环境 `compose.prod.yaml`
- [ ] 健康检查配置
- [x] 检查 Compose 服务依赖关系和端口映射
- [x] 检查生产环境是否使用 secrets 管理数据库密码和后端密钥

检查内容：

- 确认 `compose.yaml` 包含 `frontend`、`backend`、`db`、`redis` 服务。
- 确认后端依赖 MySQL 健康检查，并在启动时执行数据库迁移。
- 确认 `compose.prod.yaml` 使用 GHCR 镜像、持久化卷和 Docker secrets。
- 确认 MySQL、Redis、上传目录均配置了持久化卷。

### 3. 自动化部署

选择了选项 A：构建并推送镜像到 GHCR。

我完成的工作：

- [x] 检查 `.github/workflows/docker.yml` 的触发分支和构建矩阵
- [x] 检查前后端镜像是否分别构建
- [x] 检查 Trivy 漏洞扫描配置是否覆盖 CRITICAL/HIGH 级别问题
- [x] 补充个人贡献说明文档

## PR 链接

- PR #74: https://github.com/hzy2005/AviAI/pull/74

## 遇到的问题和解决

1. 问题：我在本次任务中没有直接实现 Dockerfile 和 Compose 的主体配置，个人贡献容易与主要实现者混淆。

   解决：在贡献说明中明确标注自己的工作范围，说明我主要负责代码检查、配置复核和文档补充，主体实现由何周屹完成。

2. 问题：Docker 配置涉及开发环境、生产环境、镜像构建、安全扫描和密钥管理，检查范围较分散。

   解决：按照作业要求拆分为 Dockerfile、Compose、自动化部署、安全配置和截图证明几个部分逐项复核。

3. 问题：前端是微信小程序，不是普通 Web 前端，Docker 部署时不能像 Vue/React 项目一样提供完整 Web 运行效果。

   解决：确认前端容器提供说明页，后端容器作为主要可访问服务，文档中说明小程序需通过微信开发者工具运行。

## AI 使用情况

- 使用 AI 辅助阅读作业要求，提炼 Dockerfile、Compose、GitHub Actions、健康检查和安全配置的检查清单。
- 使用 AI 辅助整理个人贡献说明，确保文档与实际分工一致，避免夸大个人实现内容。

## 心得体会

这次 Docker 部署任务让我认识到，容器化不只是写一个 Dockerfile，还要同时考虑镜像体积、非 root 用户、环境变量、密钥管理、服务依赖、健康检查和自动化扫描。虽然我在实现部分参与较少，但通过检查代码和补充文档，我更清楚地理解了项目从本地开发到容器化运行所需要的完整配置链路。

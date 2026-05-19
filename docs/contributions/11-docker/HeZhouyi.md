# Docker 部署贡献说明

姓名：何周屹  
学号：312190419  
日期：2026-05-19

## 我完成的工作

### 1. Dockerfile 编写

- [x] 前端 Dockerfile（多阶段构建）
- [x] 后端 Dockerfile（多阶段构建）
- [x] 前端与后端 `.dockerignore` 文件
- [x] 容器使用非 root 用户运行
- [x] 后端配置 `/health` 健康检查端点

### 2. Compose 配置

- [x] 开发环境 `compose.yaml`
- [x] 生产环境 `compose.prod.yaml`
- [x] MySQL 数据持久化卷
- [x] Redis 服务配置
- [x] 后端、数据库健康检查配置
- [x] 生产环境 secrets 密钥文件引用
- [x] 生产环境资源限制配置

### 3. 自动化部署

- 选择了选项 A：GitHub Actions 构建并推送镜像到 GHCR
- 具体内容：
  - 配置 `.github/workflows/docker.yml`
  - 使用 Docker Buildx 构建前端和后端镜像
  - 推送镜像到 GHCR
  - 使用 GitHub Actions cache 加速镜像构建
  - 集成 Trivy 对镜像进行高危漏洞扫描

## PR 链接

- PR ：https://github.com/hzy2005/AviAI/pull/74

## 遇到的问题和解决

1. 问题：项目技术栈不是作业示例中的 PostgreSQL，而是 FastAPI + MySQL + Redis。  
   解决：Compose 配置按项目实际架构使用 `mysql:8.4` 和 `redis:7-alpine`，并为 MySQL 配置数据卷和健康检查。

2. 问题：生产环境不能在 compose 文件中硬编码数据库密码和后端密钥。  
   解决：在 `compose.prod.yaml` 中使用 Docker secrets，通过 `secrets/db_password.txt`、`secrets/db_root_password.txt` 和 `secrets/backend_secret_key.txt` 注入敏感配置。

3. 问题：后端镜像如果直接安装完整开发依赖，会包含测试和 AI 模型相关依赖，镜像体积较大。  
   解决：使用 `requirements.docker.txt` 作为生产镜像依赖清单，保留 FastAPI、数据库、图片处理等运行必需依赖，避免将测试依赖和大型模型依赖打入生产镜像。

4. 问题：Docker 容器需要明确的健康检查，方便 `docker compose ps` 显示服务状态。  
   解决：后端保留 `/api/v1/health` 接口，同时增加 Docker 使用的 `/health` 端点；Compose 中通过健康检查控制服务启动顺序。

## AI 使用情况

- 使用了哪些 Prompt：
  - 为 Python FastAPI 后端创建生产级 Dockerfile，要求多阶段构建、slim 镜像、非 root 用户、健康检查和 `.dockerignore`。
  - 为微信小程序前端创建容器化 Dockerfile，要求多阶段构建、非 root 用户和健康检查。
  - 为 FastAPI + MySQL + Redis 项目创建开发和生产 Docker Compose 配置。
  - 为 Docker 镜像构建配置 GitHub Actions，并集成 GHCR 推送和 Trivy 扫描。
- AI 帮助解决了哪些问题：
  - 梳理前后端 Dockerfile 的多阶段结构。
  - 设计 MySQL、Redis、后端服务之间的依赖和健康检查。
  - 检查生产环境密钥是否硬编码。
  - 补充镜像扫描和 GHCR 推送流程。

## 心得体会

这次 Docker 部署让我更清楚地理解了开发环境和生产环境一致性的意义。后端服务不只是能本地启动，还要在容器里处理数据库迁移、健康检查、密钥注入和持久化数据。生产环境配置尤其需要关注安全边界，密码和密钥不能写死在仓库里，而应该通过 secrets 或环境变量注入。GitHub Actions 的镜像构建和漏洞扫描也让部署流程更可复现，减少了手工操作带来的不确定性。

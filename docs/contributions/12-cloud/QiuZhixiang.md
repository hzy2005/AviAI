# 云服务部署贡献说明

姓名：邱志翔
学号：2312190432
日期：2026-05-31

## 我完成的工作

### 1. 平台选择

- 使用平台：Render
- 部署对象：FastAPI 后端服务
- 选择原因：Render 支持 Docker Web Service、GitHub 自动部署和 HTTPS 访问，适合当前 `backend/Dockerfile` 部署方式。

### 2. 部署配置

- [x] 配置文件编写：新增 `render.yaml`
- [x] 后端容器适配：调整 `backend/Dockerfile`，支持 Render 动态端口 `PORT`
- [x] 数据库迁移：容器启动时执行 `alembic upgrade head`
- [ ] 环境变量配置：在 Render 控制台配置 `DATABASE_URL`、`SECRET_KEY`、`DEEPSEEK_API_KEY` 等变量
- [ ] 自动部署配置：连接 GitHub 仓库并开启 Auto Deploy
- [x] 部署说明文档：新增 `docs/deployment.md`

### 3. 问题解决

- 遇到的问题：项目后端原 Dockerfile 固定使用 8000 端口，而 Render Web Service 会通过 `PORT` 环境变量分配运行端口。
- 解决方案：将 Uvicorn 启动命令改为读取 `${PORT:-8000}`，保证 Render 和本地 Docker 都可以启动。

- 遇到的问题：云端首次启动时数据库可能还没有创建表结构。
- 解决方案：在容器启动命令中先执行 `alembic upgrade head`，再启动 FastAPI 服务。

- 遇到的问题：前端是原生微信小程序，不适合直接作为普通 Web 前端部署到 Vercel。
- 解决方案：后端部署到 Render，前端通过微信开发者工具上传体验版或发布版，并将请求域名配置为 Render HTTPS 地址。

## PR 链接

- PR #X: https://github.com/hzy2005/AviAI/pull/X

## 在线地址

部署完成后填写：

```text
https://<render-service-domain>
```

健康检查地址：

```text
https://<render-service-domain>/api/v1/health
```

## 心得体会

这次部署让我把本地开发环境和线上运行环境之间的差异梳理得更清楚。后端云部署不仅要能构建镜像，还要处理端口、环境变量、数据库迁移和健康检查等生产环境问题。通过 Render 连接 GitHub 自动部署后，项目从提交代码到线上更新形成了完整流程，也更符合真实项目的交付方式。


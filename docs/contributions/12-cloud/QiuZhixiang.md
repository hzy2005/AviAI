# 云服务部署贡献说明

姓名：邱志翔
学号：2312190432
日期：2026-05-31

## 我完成的工作

### 1. 平台选择

- 使用平台：Render
- 部署对象：FastAPI 后端服务
- 数据库：云 MySQL
- 前端验证方式：微信开发者工具运行原生微信小程序，并请求 Render 后端接口

选择 Render 的原因：

- Render 支持 Docker Web Service，适合当前项目已有的 `backend/Dockerfile`。
- Render 可以连接 GitHub 仓库，实现推送后自动部署。
- Render 自动提供 HTTPS 域名，便于小程序前端请求线上后端。

### 2. 部署配置

- [x] 编写 Render 部署配置文件：`render.yaml`
- [x] 调整后端 Docker 启动命令，支持 Render 动态端口 `PORT`
- [x] 容器启动时执行数据库迁移：`alembic upgrade head`
- [x] 在 Render 控制台配置环境变量
- [x] 配置云 MySQL，并通过 `DATABASE_URL` 连接后端服务
- [x] 连接 GitHub 仓库并开启 Auto Deploy
- [x] 使用 `feature/QiuZhixiang-cloud` 分支完成首次部署验证
- [x] PR 合并到 `develop` 后，将 Render 部署分支切换为 `develop`
- [x] 新增部署说明文档：`docs/deployment.md`
- [x] 修改小程序前端配置，使接口请求指向 Render 后端：`frontend/config/env.js`

### 3. 环境变量配置

Render 中配置的主要环境变量：

- `DATABASE_URL`
- `SECRET_KEY`
- `USE_MOCK_DATA=false`
- `ACCESS_TOKEN_EXPIRE_MINUTES=10080`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL=https://api.deepseek.com/v1`
- `DEEPSEEK_MODEL=deepseek-chat`
- `DEEPSEEK_VISION_MODEL=deepseek-chat`

敏感信息只配置在 Render 控制台，没有写入仓库。

### 4. 部署验证

后端在线地址：

```text
https://aviai-backend.onrender.com
```

健康检查地址：

```text
https://aviai-backend.onrender.com/api/v1/health
```

健康检查结果显示：

- 后端服务状态：`running`
- 数据库连接状态：`connected`

FastAPI 文档地址：

```text
https://aviai-backend.onrender.com/docs
```

### 5. 前端接入验证

前端为原生微信小程序，不适合作为普通 Web 项目部署到 Vercel。当前前端采用微信开发者工具运行，并将后端接口地址配置为：

```text
https://aviai-backend.onrender.com
```

在微信开发者工具 Network 面板中，已验证登录等接口请求访问的是 Render 后端，例如：

```text
https://aviai-backend.onrender.com/api/v1/auth/login
```

同时，开发者工具中出现的如下地址属于本地小程序静态资源预览地址，不是后端接口地址：

```text
http://127.0.0.1:<port>/__pageframe__/static/...
```

本次使用的是小程序测试号。测试号支持本地开发调试，但不支持完整的体验版上传和正式发布流程，因此本次前端验证以微信开发者工具运行截图和 Network 请求截图作为证明。

### 6. 问题解决

问题 1：Render 会通过 `PORT` 环境变量分配运行端口，原 Dockerfile 固定使用 8000 端口。

解决方案：将 Uvicorn 启动命令改为：

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

问题 2：云端首次启动时数据库表结构可能还不存在。

解决方案：在容器启动时先执行：

```bash
alembic upgrade head
```

再启动 FastAPI 服务。

问题 3：前端是原生微信小程序，不能像普通 Web 前端一样直接部署到 Vercel 并在线访问完整功能。

解决方案：后端部署到 Render，前端在微信开发者工具中运行，并将请求地址切换到 Render 后端。

问题 4：当前使用的小程序测试号无法上传体验版。

解决方案：使用微信开发者工具本地运行进行验证，并保留 Network 请求截图，证明前端已接入线上后端。

## PR 链接

- PR #78: https://github.com/hzy2005/AviAI/pull/78

## 在线地址

```text
https://aviai-backend.onrender.com
```

健康检查地址：

```text
https://aviai-backend.onrender.com/api/v1/health
```

## 截图证明

学习通提交时准备以下截图：

- Git 提交记录截图：`git log --author="QiuZhixiang" --oneline --graph`
- Render 部署成功截图：`/api/v1/health` 返回 `database: connected`
- Render 环境变量配置截图：敏感值打码，变量名保留
- 微信开发者工具运行截图
- Network 面板请求 Render 后端接口截图

## 心得体会

这次云服务部署让我完整体验了从本地开发到线上访问的流程。后端部署不仅需要能启动服务，还需要处理动态端口、环境变量、数据库连接、数据库迁移和健康检查等问题。通过 Render 连接 GitHub 后，项目可以在分支更新后自动部署，形成了更接近真实项目的交付流程。

前端部分也让我认识到原生微信小程序与普通 Web 前端的部署方式不同。小程序更适合通过微信开发者工具和微信小程序平台发布，本次由于使用测试号，最终采用本地运行加线上接口请求的方式完成验证。

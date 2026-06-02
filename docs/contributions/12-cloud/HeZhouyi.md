# 云服务部署贡献说明

姓名：何周屹
学号：2312190419
日期：2026-06-02

## 我完成的工作

### 1. 平台选择

- 使用平台：Render
- 部署对象：FastAPI 后端服务
- 数据库：云 MySQL
- 前端验证方式：微信开发者工具运行原生微信小程序，并请求 Render 线上后端接口

我参与核对了当前项目的部署方案，确认原生微信小程序不适合作为普通 Web 页面直接部署，后端部署到 Render、前端在微信开发者工具中接入线上后端更符合项目实际情况。

### 2. 部署配置

- [x] 核对 Render 部署配置文件：`render.yaml`
- [x] 核对后端 Docker 启动命令支持 Render 动态端口 `PORT`
- [x] 核对容器启动时执行数据库迁移：`alembic upgrade head`
- [x] 核对 Render 环境变量配置项
- [x] 核对云 MySQL 连接方式：`DATABASE_URL`
- [x] 核对自动部署配置：Render 连接 GitHub 仓库并开启 Auto Deploy
- [x] 核对小程序前端线上接口地址：`frontend/config/env.js`
- [x] 同步完善 API 文档中健康检查和监控指标接口说明：`docs/api.md`、`docs/api.yaml`
- [x] 在后端 README 中补充验收常用接口：`backend/README.md`

### 3. 环境变量配置

Render 中需要配置的主要环境变量包括：

- `DATABASE_URL`
- `SECRET_KEY`
- `USE_MOCK_DATA=false`
- `ACCESS_TOKEN_EXPIRE_MINUTES=10080`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL=https://api.deepseek.com/v1`
- `DEEPSEEK_MODEL=deepseek-chat`
- `DEEPSEEK_VISION_MODEL=deepseek-chat`

我重点核对了敏感信息管理方式，确认真实数据库密码、JWT 密钥和第三方 API Key 只应配置在 Render 控制台，不应写入仓库。

### 4. 部署验证

后端在线地址：

```text
https://aviai-backend.onrender.com
```

API 健康检查地址：

```text
https://aviai-backend.onrender.com/api/v1/health
```

平台健康检查地址：

```text
https://aviai-backend.onrender.com/health
```

验证结果：

- `/api/v1/health` 返回统一响应结构，服务状态为 `running`
- `/health` 返回简洁健康检查结构，服务状态为 `healthy`
- 数据库连接状态为 `connected`

### 5. 前端接入验证

我在微信开发者工具的 Network 面板中核对了小程序请求地址，确认登录接口请求发送到 Render 后端：

```text
https://aviai-backend.onrender.com/api/v1/auth/login
```

其中 `png`、`svg` 等请求为小程序静态资源加载；`login`、`me` 等 `xhr` 请求才是后端接口调用，可作为前端接入线上后端的辅助证明。

### 6. 问题解决

1. 问题：作业要求应用在线访问成功，但项目是原生微信小程序，不能按普通 Web 前端直接部署。

   解决：采用后端 Render 在线部署、小程序本地开发者工具接入线上接口的方式完成验证，并保留 Network 请求截图证明。

2. 问题：API 文档中 `/health` 的描述与实际返回结构不一致，容易影响验收理解。

   解决：将 `docs/api.md` 和 `docs/api.yaml` 中 `/health`、`/api/v1/health`、`/api/v1/metrics` 的描述统一为实际后端返回结构。

3. 问题：验收者需要快速找到监控相关接口。

   解决：在 `backend/README.md` 中补充 `/health`、`/api/v1/health` 和 `/api/v1/metrics`。

## PR 链接

- PR #待补充：https://github.com/hzy2005/AviAI/pull/待补充

## 在线地址

```text
https://aviai-backend.onrender.com
```

健康检查地址：

```text
https://aviai-backend.onrender.com/api/v1/health
https://aviai-backend.onrender.com/health
```

## 心得体会

这次云服务部署让我更清楚地理解了线上交付不只是“代码能运行”，还包括 Docker 启动命令、动态端口、环境变量、数据库迁移、健康检查和前端线上接口切换等环节。对于原生微信小程序项目，前端验证方式也需要结合微信开发者工具和小程序平台的实际限制来设计，不能简单套用普通 Web 前端部署流程。

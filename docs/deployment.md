# AviAI 云服务部署说明

## 1. 部署方案

本项目采用前后端分离部署：

- 后端：FastAPI 服务部署到 Render Web Service。
- 前端：原生微信小程序，通过微信开发者工具上传体验版或发布版，接口地址指向线上后端。
- 数据库：使用云 MySQL，后端通过 `DATABASE_URL` 环境变量连接。

选择 Render 的原因：

- 支持 Docker 部署，适合当前已有的 `backend/Dockerfile`。
- 可以连接 GitHub 仓库并在推送后自动部署。
- 自动提供 HTTPS 域名，便于微信小程序配置 request 合法域名。

## 2. 部署配置文件

本仓库根目录提供 `render.yaml`，核心配置如下：

- 服务类型：Web Service
- 运行方式：Docker
- Docker 构建上下文：`backend`
- Dockerfile：`backend/Dockerfile`
- 健康检查路径：`/api/v1/health`
- 自动部署：开启

后端容器启动时会先执行数据库迁移：

```bash
alembic upgrade head
```

然后使用 Render 提供的 `PORT` 环境变量启动 Uvicorn：

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## 3. Render 部署步骤

1. 登录 Render 控制台。
2. 选择 New > Blueprint 或 New > Web Service。
3. 连接 GitHub 仓库 `AviAI`。
4. 选择部署分支：
   - 作业验证阶段：选择个人云部署分支 `feature/QiuZhixiang-cloud`。
   - 合并联调阶段：PR 合并到 `develop` 后，将 Render 服务的部署分支切换为 `develop`。
   - 最终发布阶段：`develop` 合并到 `master` 后，可将生产服务的部署分支切换为 `master`，或保留 `develop` 作为开发环境服务。
5. 使用仓库中的 `render.yaml` 创建服务。
6. 在 Render 的 Environment 页面配置环境变量。
7. 点击 Deploy，等待构建和启动完成。
8. 访问以下地址验证部署结果：

```text
https://<render-service-domain>/api/v1/health
```

成功响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "service": "backend",
    "status": "running",
    "database": "connected"
  }
}
```

## 4. 环境变量

Render 后端服务需要配置以下环境变量：

| 变量名 | 示例 | 说明 |
| --- | --- | --- |
| `DATABASE_URL` | `mysql+pymysql://user:password@host:3306/aviai?charset=utf8mb4` | 云 MySQL 连接地址 |
| `SECRET_KEY` | Render 自动生成或手动填写长随机字符串 | JWT 签名密钥 |
| `USE_MOCK_DATA` | `false` | 生产环境使用真实数据库 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | Token 有效期 |
| `DEEPSEEK_API_KEY` | `sk-xxxx` | 第三方 AI 服务密钥 |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com/v1` | DeepSeek API 地址 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | 文本模型 |
| `DEEPSEEK_VISION_MODEL` | `deepseek-chat` | 图片相关模型配置 |
| `SENTRY_DSN` | `https://xxx@o000000.ingest.sentry.io/0000000` | Sentry 错误追踪 DSN，可选 |
| `SENTRY_ENVIRONMENT` | `production` | Sentry 环境名称，可选 |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.0` | Sentry 性能追踪采样率，可选 |

注意：

- 不要把真实数据库密码、`SECRET_KEY`、`DEEPSEEK_API_KEY`、`SENTRY_DSN` 写入仓库。
- 截图提交时可以打码变量值，但变量名需要清晰可见。

## 5. 前端接入线上后端

微信小程序前端不部署为普通 Web 页面。上线或体验版验证时，需要在 `frontend/config/env.js` 中将请求地址配置为 Render 后端 HTTPS 地址，例如：

```js
const PROD_BASE_URL = "https://<render-service-domain>";
```

同时需要在微信公众平台配置 request 合法域名：

```text
https://<render-service-domain>
```

## 6. 自动部署

Render 与 GitHub 仓库连接后，开启 Auto Deploy：

- 推送到当前绑定的部署分支后自动构建 Docker 镜像。
- 构建成功后自动启动新版本服务。
- 可在 Render Events 页面查看部署记录。

当前分支流转建议：

1. 在 `feature/QiuZhixiang-cloud` 分支完成部署验证，并提交作业截图。
2. 创建 PR，将 `feature/QiuZhixiang-cloud` 合并到 `develop`。
3. 合并后进入 Render 服务的 Settings 页面，将 Branch 从 `feature/QiuZhixiang-cloud` 改为 `develop`，然后执行一次 Manual Deploy。
4. 当 `develop` 最终合并到 `master` 后，如果需要生产环境跟随 `master`，再将 Render Branch 改为 `master`。

本项目也保留了 GitHub Actions 中的 CI 和 Docker 构建检查，用于在云部署前发现测试、Lint 和镜像构建问题。

## 7. 验收截图

学习通提交建议准备以下截图：

1. Git 提交记录截图：

```bash
git log --author="QiuZhixiang" --oneline --graph
```

2. 部署成功截图：

```text
https://<render-service-domain>/api/v1/health
```

3. 环境变量配置截图：

```text
Render Dashboard > aviai-backend > Environment
```

4. 可用性告警截图（可选）：

```text
UptimeRobot Dashboard > AviAI Backend Health
```

5. 在线地址：

```text
https://<render-service-domain>
```

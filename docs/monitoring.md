# AviAI 监控配置说明

## 1. 监控目标

本次监控配置用于为已部署的 AviAI 后端服务建立基础可观测性，覆盖以下内容：

- 结构化 JSON 日志
- 健康检查端点
- 基础指标收集
- Sentry 错误追踪（可选）
- UptimeRobot 可用性告警（可选）
- Render 部署环境中的日志查看和截图验证

## 2. 结构化日志

后端新增日志工具：

```text
backend/app/utils/logger.py
```

日志使用 JSON 格式输出到标准输出，便于在本地终端、Docker 日志和 Render Logs 中查看。
同时，后端会接管 `uvicorn`、`uvicorn.error` 和 `uvicorn.access` logger，使 Uvicorn 访问日志也使用同一套 JSON 格式，避免 Render Logs 中混入默认文本日志。

请求日志字段包括：

| 字段 | 说明 |
| --- | --- |
| `time` | UTC 日志时间 |
| `level` | 日志级别 |
| `message` | 日志消息 |
| `module` | 输出日志的模块 |
| `logger` | logger 名称 |
| `method` | HTTP 请求方法 |
| `path` | 请求路径 |
| `status_code` | HTTP 响应状态码 |
| `duration_ms` | 请求耗时，单位毫秒 |
| `client` | 客户端地址 |

示例：

```json
{
  "time": "2026-05-31T09:00:00+00:00",
  "level": "INFO",
  "message": "request completed",
  "module": "main",
  "logger": "app.main",
  "method": "GET",
  "path": "/health",
  "status_code": 200,
  "duration_ms": 8.52,
  "client": "127.0.0.1"
}
```

## 3. 健康检查

### 3.1 平台健康检查

新增直接健康检查端点：

```text
GET /health
```

返回示例：

```json
{
  "status": "healthy",
  "timestamp": "2026-05-31T09:00:00+00:00",
  "version": "0.3.0",
  "database": "connected"
}
```

该端点适合 Render、Docker 和截图验收使用。

### 3.2 API 健康检查

保留原有统一响应结构健康检查：

```text
GET /api/v1/health
```

返回示例：

```json
{
  "code": 0,
  "msg": "success",
  "message": "success",
  "data": {
    "service": "backend",
    "status": "running",
    "database": "connected",
    "time": "2026-05-31T09:00:00+00:00"
  }
}
```

## 4. 基础指标

新增指标接口：

```text
GET /api/v1/metrics
```

当前指标使用进程内存统计，适合课程作业和单实例部署验证。

返回字段：

| 字段 | 说明 |
| --- | --- |
| `requestCount` | 已处理请求总数 |
| `errorCount` | 5xx 错误请求数 |
| `errorRate` | 错误率 |
| `averageResponseMs` | 平均响应时间，单位毫秒 |
| `activeRequests` | 当前活跃请求数 |
| `statusCodes` | 各 HTTP 状态码计数 |

返回示例：

```json
{
  "code": 0,
  "msg": "success",
  "message": "success",
  "data": {
    "requestCount": 12,
    "errorCount": 0,
    "errorRate": 0.0,
    "averageResponseMs": 9.41,
    "activeRequests": 1,
    "statusCodes": {
      "200": 12
    }
  }
}
```

## 5. Render 日志查看

部署到 Render 后，可以在以下位置查看结构化日志：

```text
Render Dashboard > aviai-backend > Logs
```

访问 `/health`、`/api/v1/health` 或其他接口后，Logs 中会输出 JSON 请求日志，可作为学习通“日志输出截图”。

## 6. Sentry 错误追踪（可选）

后端支持可选接入 Sentry，用于捕获未处理异常并在 Sentry 控制台中追踪错误。

相关配置文件：

```text
backend/app/utils/sentry.py
```

当 `SENTRY_DSN` 为空时，后端会跳过 Sentry 初始化，不影响本地开发、测试或普通部署；当在 Render 环境变量中配置 `SENTRY_DSN` 后，服务启动时会自动初始化 Sentry FastAPI 集成。

Render 建议配置：

| 变量名 | 示例 | 说明 |
| --- | --- | --- |
| `SENTRY_DSN` | `https://xxx@o000000.ingest.sentry.io/0000000` | Sentry 项目的 DSN，敏感值需打码 |
| `SENTRY_ENVIRONMENT` | `production` | Sentry 环境名称 |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.0` | 性能追踪采样率，课程作业可保持 0，仅启用错误追踪 |

## 7. 可用性告警（可选）

为了覆盖“服务不可用告警”场景，可以使用 Render 健康检查配合 UptimeRobot 外部监控。

### 7.1 Render 健康检查

Render 部署配置中已设置健康检查路径：

```text
/api/v1/health
```

Render 会根据该路径判断服务是否健康，可在 Render Dashboard 的服务状态、Events 或 Logs 页面查看部署和健康检查相关信息。

### 7.2 UptimeRobot 告警配置

推荐在 UptimeRobot 中新增 HTTP(s) Monitor：

| 配置项 | 建议值 |
| --- | --- |
| Monitor Type | HTTP(s) |
| Friendly Name | `AviAI Backend Health` |
| URL | `https://aviai-backend.onrender.com/health` |
| Monitoring Interval | `5 minutes` |
| Alert Contact | 个人邮箱 |

告警验证方式：

- UptimeRobot 监控列表中显示服务状态为 `Up`
- Monitor Detail 页面显示最近检查成功
- Alert Contact 已绑定邮箱

学习通提交时可将 UptimeRobot Monitor Detail 页面作为“服务不可用告警配置”截图；如果不提交该选做项，不影响基础监控要求。

## 8. 验收截图

学习通提交建议准备以下截图：

1. Git 提交记录截图：

```bash
git log --author="QiuZhixiang" --oneline --graph
```

2. 健康检查端点截图：

```text
https://aviai-backend.onrender.com/health
```

3. 日志输出截图：

```text
Render Dashboard > aviai-backend > Logs
```

4. 指标接口截图：

```text
https://aviai-backend.onrender.com/api/v1/metrics
```

5. Sentry 配置截图（可选）：

```text
Render Dashboard > aviai-backend > Environment > SENTRY_DSN
```

或 Sentry 控制台中项目 Issues 页面截图。

6. UptimeRobot 告警截图（可选）：

```text
UptimeRobot Dashboard > AviAI Backend Health
```

截图中建议包含监控 URL、状态 `Up`、检查间隔和告警联系人。

## 9. 后续扩展

当前实现为基础监控配置。后续可以继续扩展：

- 接入 Prometheus / Grafana 进行长期指标存储和可视化
- 继续细化 Render 或第三方平台告警规则，覆盖错误率升高、响应时间变慢等场景

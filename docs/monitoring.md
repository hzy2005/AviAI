# AviAI 监控配置说明

## 1. 监控目标

本次监控配置用于为已部署的 AviAI 后端服务建立基础可观测性，覆盖以下内容：

- 结构化 JSON 日志
- 健康检查端点
- 基础指标收集
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

## 6. 验收截图

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

## 7. 后续扩展

当前实现为基础监控配置。后续可以继续扩展：

- 接入 Prometheus / Grafana 进行长期指标存储和可视化
- 接入 Sentry 进行错误追踪
- 配置 Render 或第三方平台告警，覆盖服务不可用和错误率升高场景

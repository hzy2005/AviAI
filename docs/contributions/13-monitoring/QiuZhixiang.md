# 监控配置贡献说明

姓名：邱志翔
学号：2312190432
日期：2026-05-31

## 我完成的工作

### 1. 日志配置

- [x] 结构化日志格式
- [x] 日志级别配置
- [x] 请求日志中间件

具体内容：

- 新增 `backend/app/utils/logger.py`。
- 实现 `JsonFormatter`，将日志输出为 JSON 格式。
- 在请求日志中记录请求方法、路径、状态码、响应时间和客户端地址。
- 将日志输出到标准输出，方便在本地终端、Docker 日志和 Render Logs 中查看。

### 2. 健康检查

- [x] `/health` 端点实现
- [x] `/api/v1/health` 端点保留
- [x] 数据库连接检查逻辑

具体内容：

- 新增 `/health`，返回适合平台健康检查和截图验收的简洁结构。
- 保留原有 `/api/v1/health`，继续使用项目统一响应结构。
- 健康检查中执行 `SELECT 1` 判断数据库连接状态。

### 3. 指标收集

- [x] 请求计数
- [x] 响应时间
- [x] 错误率
- [x] 状态码计数
- [x] 活跃请求数

具体内容：

- 新增 `backend/app/utils/metrics.py`。
- 使用进程内存记录基础指标。
- 新增 `/api/v1/metrics` 指标接口。
- 指标返回 `requestCount`、`errorCount`、`errorRate`、`averageResponseMs`、`activeRequests` 和 `statusCodes`。

### 4. 文档说明

- [x] 新增 `docs/monitoring.md`
- [x] 补充日志字段说明
- [x] 补充健康检查端点说明
- [x] 补充指标接口说明
- [x] 补充学习通截图清单

## PR 链接

- PR #X: https://github.com/hzy2005/AviAI/pull/79

## 遇到的问题和解决

1. 问题：项目原来已有 `/api/v1/health`，但作业要求明确演示 `/health` 端点。

   解决：保留 `/api/v1/health` 不破坏原有 API 契约，同时新增 `/health` 返回简洁健康检查结构。

2. 问题：基础指标需要统计请求计数、响应时间和错误率，但项目暂时没有引入 Prometheus 等监控依赖。

   解决：实现轻量级内存指标收集器，满足课程作业的基础监控要求，后续可扩展为 Prometheus/Grafana。

3. 问题：日志需要方便在 Render 中截图查看。

   解决：将结构化 JSON 日志输出到标准输出，Render Logs 可以直接展示请求日志。

## 验证结果

本地验证：

```bash
pytest backend/tests -c backend/pytest.ini
```

需要截图验证的地址：

```text
https://aviai-backend.onrender.com/health
https://aviai-backend.onrender.com/api/v1/metrics
```

日志截图位置：

```text
Render Dashboard > aviai-backend > Logs
```

## 心得体会

这次监控配置让我理解到，应用上线后不能只关注“能不能访问”，还需要知道服务是否健康、请求是否变慢、错误是否增加。结构化日志可以让问题排查更直接，健康检查可以帮助平台判断服务状态，基础指标则可以让运行情况变得可观察。虽然这次实现的是轻量级监控，但已经覆盖了线上服务最基础的可观测性需求。

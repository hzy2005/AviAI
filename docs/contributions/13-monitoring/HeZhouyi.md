# 监控配置贡献说明

姓名：何周屹
学号：2312190419
日期：2026-06-02

## 我完成的工作

### 1. 日志配置

- [x] 核对结构化 JSON 日志格式
- [x] 核对日志级别配置
- [x] 核对请求日志中间件
- [x] 核对 Render Logs 中的日志截图方式

具体内容：

- 核对 `backend/app/utils/logger.py` 中的 `JsonFormatter` 实现。
- 确认日志输出到标准输出，便于在本地终端、Docker 日志和 Render Logs 中查看。
- 确认请求日志包含 `time`、`level`、`message`、`module`、`logger`、`method`、`path`、`status_code`、`duration_ms` 和 `client` 等字段。
- 整理了学习通提交时“日志输出截图”的获取方式：访问 `/health` 后，在 Render Dashboard > `aviai-backend` > Logs 中截取 JSON 日志。

### 2. 健康检查

- [x] `/health` 端点实现
- [x] `/api/v1/health` 端点保留
- [x] 数据库连接检查逻辑
- [x] 健康检查文档同步

具体内容：

- 核对 `/health` 返回适合平台健康检查和截图验收的简洁结构。
- 核对 `/api/v1/health` 返回项目统一响应结构。
- 确认健康检查中会执行 `SELECT 1` 判断数据库连接状态。
- 在线访问验证健康检查接口，确认返回 `healthy` / `running` 和 `database: connected`。

### 3. 指标收集

- [x] 请求计数
- [x] 响应时间
- [x] 错误率
- [x] 状态码计数
- [x] 活跃请求数
- [x] 指标接口文档同步

具体内容：

- 核对 `backend/app/utils/metrics.py` 中的轻量级内存指标收集器。
- 确认请求中间件会统计请求数量、响应耗时、5xx 错误数和状态码分布。
- 核对 `/api/v1/metrics` 指标接口返回 `requestCount`、`errorCount`、`errorRate`、`averageResponseMs`、`activeRequests` 和 `statusCodes`。
- 在 `docs/api.md`、`docs/api.yaml` 和 `backend/README.md` 中同步补充健康检查和指标接口说明，方便验收者快速定位。

### 4. 文档说明

- [x] 核对 `docs/monitoring.md`
- [x] 补充 API 文档中 `/health` 与 `/api/v1/health` 的区别
- [x] 补充 API 文档中 `/api/v1/metrics` 的返回结构
- [x] 补充后端 README 中的监控入口
- [x] 补充可选 Prometheus 文本格式指标接口
- [x] 补充可选 Sentry 错误追踪配置
- [x] 补充可选 UptimeRobot 服务可用性告警配置
- [x] 整理学习通截图清单

## PR 链接

- PR #待补充：https://github.com/hzy2005/AviAI/pull/待补充

## 遇到的问题和解决

1. 问题：`/health` 和 `/api/v1/health` 容易混淆。

   解决：明确区分根路径 `/health` 是平台健康检查，不使用统一响应包裹；`/api/v1/health` 是 API 健康检查，使用 `code/msg/message/data` 统一响应结构。

2. 问题：作业要求日志输出截图，但日志不是浏览器页面直接展示。

   解决：先访问线上 `/health` 触发请求日志，再进入 Render Dashboard > `aviai-backend` > Logs 截取 JSON 日志。

3. 问题：指标收集是评分项，但原后端 README 没有列出指标接口。

   解决：在 `backend/README.md` 中补充 `GET /api/v1/metrics`，并在 API 文档中补充指标字段说明。

4. 问题：当前 `/api/v1/metrics` 是 JSON 结构，适合课程验收，但不方便 Prometheus / Grafana 直接抓取。

   解决：新增根路径 `GET /metrics`，输出 Prometheus text exposition 格式，并在 `docs/monitoring.md` 中补充 Prometheus 抓取配置示例。

5. 问题：错误追踪是作业选做项，但不能强制依赖真实 DSN，否则本地测试和普通部署会受影响。

   解决：新增可选 Sentry 配置，只有配置 `SENTRY_DSN` 时才初始化 Sentry；未配置时自动跳过，不影响服务启动。

6. 问题：服务上线后还需要知道“什么时候不可用”，但项目本身没有独立告警系统。

   解决：在 `docs/monitoring.md` 中补充 UptimeRobot 外部 HTTP(s) 监控方案，监控 `https://aviai-backend.onrender.com/health`，并通过邮箱告警覆盖服务不可用场景。

## 验证结果

线上健康检查：

```text
https://aviai-backend.onrender.com/health
```

返回结果包含：

- `status: healthy`
- `version: 0.3.0`
- `database: connected`

线上指标接口：

```text
https://aviai-backend.onrender.com/api/v1/metrics
```

返回结果包含：

- `requestCount`
- `errorCount`
- `errorRate`
- `averageResponseMs`
- `activeRequests`
- `statusCodes`

文档校验：

```bash
python -c "import pathlib, yaml; yaml.safe_load(pathlib.Path('docs/api.yaml').read_text(encoding='utf-8')); print('api.yaml parsed')"
git diff --check -- docs/api.md docs/api.yaml backend/README.md
```

校验结果：`api.yaml parsed`，无空白错误。

## 截图证明

学习通提交时准备以下截图：

- Git 提交记录截图：`git log --author="HeZhouyi" --oneline --graph`
- 健康检查端点截图：浏览器访问 `https://aviai-backend.onrender.com/health`
- 日志输出截图：Render Dashboard > `aviai-backend` > Logs 中的 JSON 请求日志
- 指标接口截图：浏览器访问 `https://aviai-backend.onrender.com/api/v1/metrics`
- Prometheus 指标截图（可选）：浏览器访问 `https://aviai-backend.onrender.com/metrics`
- UptimeRobot 告警配置截图（可选）：Monitor Detail 页面显示 URL、状态 `Up` 和告警联系人

## 心得体会

这次监控配置让我认识到，应用上线后还需要能够被观察和验证。健康检查能帮助平台判断服务是否可用，结构化日志能帮助定位每一次请求的状态和耗时，基础指标能反映请求量、错误率和响应时间。虽然当前实现是适合课程作业和单实例部署的轻量级方案，但已经覆盖了线上服务最基本的可观测性要求。

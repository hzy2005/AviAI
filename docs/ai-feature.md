# AI 功能说明

## 1. 使用模型

当前后端通过 DeepSeek 接口实现 AI 文案能力，模型由环境变量配置：

- 文本模型：`DEEPSEEK_MODEL`（默认：`deepseek-chat`）
- 视觉模型：`DEEPSEEK_VISION_MODEL`（默认`deepseek-chat`）

相关参数：

- `DEEPSEEK_TEXT_TEMPERATURE`
- `DEEPSEEK_TEXT_MAX_TOKENS`
- `DEEPSEEK_VISION_TEMPERATURE`
- `DEEPSEEK_VISION_MAX_TOKENS`
- `DEEPSEEK_TIMEOUT_SECONDS`

## 2. 已实现功能

### 2.1 社区发帖 AI 文案辅助

接口：`POST /api/v1/posts/ai-copywriting`

- `mode=generate`：用户只上传图片时，自动生成分享文案
- `mode=polish`：用户已填写文案时，对现有文案润色

### 2.2 图片先上传再生成

接口：`POST /api/v1/posts/upload-image`

- 前端先上传图片，拿到 `/uploads/...`
- 再调用 `ai-copywriting`，确保后端可访问图片并进行视觉推理

### 2.3 生成质量与稳定性增强

- 结合鸟类识别结果（`birdName/confidence`）作为提示上下文
- 支持视觉输入（图片以 URL 或 base64 data URL 形式传入模型）
- 输出结构约束（场景 + 观察 + 感受）与长度约束
- 结果质量检查（最小长度、重复词、模板化短语过滤）+ 一次自动重试
- 生成失败时 fallback，保证接口可用性

### 2.4 润色能力增强

- 润色遵循“保留原意、不新增事实、提升流畅度和可读性”
- 返回双版本：
  - `lite`（轻润色）
  - `enhanced`（增强润色）
- 兼容旧前端：`data.content` 默认等于 `lite`

### 2.5 可观测性

`ai-copywriting` 返回 `aiMeta`，用于定位效果与性能问题，包含：

- `mode`
- `model`
- `elapsedMs`
- `retryCount`
- `fallback`
- `params.text / params.vision`
- `birdHint`、`visionFacts`、`visualHint`（用于排查“文案是否贴图”）

## 3. 最小调用流程

1. 前端选择图片并调用 `POST /api/v1/posts/upload-image`
2. 前端拿到 `imageUrl=/uploads/...`
3. 调用 `POST /api/v1/posts/ai-copywriting`
4. 将返回文案回填到发帖输入框，用户确认后发布

# AviAI API 文档（api.md）

## 1. 文档说明

本项目 API 按 OpenAPI 3.0 维护，机器可读规范见 [api.yaml](./api.yaml)。  
本文件用于前后端联调时快速确认“实际契约”，字段和状态码以 `api.yaml` 为准。

- 基础路径：`/api/v1`
- 数据格式：`application/json`
- 鉴权方式：`Authorization: Bearer <token>`
- 时间格式：ISO 8601（例如 `2026-03-09T10:30:00Z`）

## 2. 统一响应结构

成功响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

错误响应：

```json
{
  "code": 1001,
  "message": "参数错误",
  "data": null
}
```

常见错误码：

- `0`：成功
- `1001`：参数错误
- `1002`：未登录或 Token 无效
- `1003`：无权限
- `1004`：资源不存在
- `1005`：服务内部错误
- `1006`：上传文件不合法
- `1009`：资源冲突（如重复注册、重复点赞）

## 3. 接口总览

| 模块 | 方法 | 路径 | 鉴权 | 说明 |
| --- | --- | --- | --- | --- |
| Health | GET | `/health` | 否 | 服务健康检查 |
| Auth | POST | `/auth/register` | 否 | 用户注册 |
| Auth | POST | `/auth/login` | 否 | 用户登录 |
| Auth | POST | `/auth/logout` | 否 | 用户登出 |
| Users | GET | `/users/me` | 是 | 当前用户信息 |
| Birds | POST | `/birds/recognize` | 是 | 上传图片识别 |
| Birds | GET | `/birds/records` | 是 | 识别记录分页 |
| Posts | POST | `/posts` | 是 | 发布动态 |
| Posts | POST | `/posts/ai-copywriting` | 是 | AI 生成/润色社区文案 |
| Posts | GET | `/posts` | 否 | 动态分页列表（支持 keyword） |
| Posts | GET | `/posts/{postId}` | 否 | 动态详情 |
| Posts | PUT | `/posts/{postId}` | 是 | 更新动态（仅作者） |
| Posts | DELETE | `/posts/{postId}` | 是 | 删除动态（仅作者） |
| Posts | POST | `/posts/{postId}/like` | 是 | 点赞动态 |
| Posts | POST | `/posts/{postId}/comments` | 是 | 评论动态 |

## 4. 前端关键契约

### 4.1 Auth

`POST /api/v1/auth/login` 返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "token": "jwt-token",
    "user": {
      "id": 1,
      "username": "birdlover",
      "avatarUrl": ""
    }
  }
}
```

`GET /api/v1/users/me` 返回 `userProfile`：

```json
{
  "id": 1,
  "username": "birdlover",
  "email": "bird@example.com",
  "avatarUrl": "",
  "createdAt": "2026-03-09T10:30:00Z"
}
```

### 4.2 Birds

`POST /api/v1/birds/recognize`  
`Content-Type: multipart/form-data`，字段名 `image`。

返回字段固定为：

```json
{
  "recordId": 101,
  "birdName": "白鹭",
  "confidence": 0.9342,
  "imageUrl": "/uploads/20260309_xxx.jpg",
  "createdAt": "2026-03-09T10:35:00Z"
}
```

`GET /api/v1/birds/records?page=1&pageSize=10` 返回分页结构：

```json
{
  "list": [],
  "total": 0,
  "page": 1,
  "pageSize": 10
}
```

### 4.3 Posts（列表/详情）

`GET /api/v1/posts` 和 `GET /api/v1/posts/{postId}` 的帖子对象字段固定为：

```json
{
  "postId": 1001,
  "content": "今天在湿地拍到了白鹭",
  "imageUrl": "/uploads/post_001.jpg",
  "likeCount": 12,
  "commentCount": 3,
  "createdAt": "2026-03-09T12:00:00Z",
  "updatedAt": "2026-03-09T12:30:00Z",
  "author": {
    "id": 1,
    "username": "birdlover",
    "avatarUrl": ""
  }
}
```

### 4.4 Posts（AI 文案辅助）

`POST /api/v1/posts/ai-copywriting` 用于社区发帖前的 AI 文案辅助，服务端内部调用 DeepSeek API 生成结果；前端拿到返回文案后，仍通过 `POST /api/v1/posts` 完成最终发布。

支持两种模式：

- `generate`：用户仅上传图片，AI 基于图片生成社区文案
- `polish`：用户上传图片并填写原始文案，AI 对文案进行润色

请求体：

```json
{
  "mode": "generate",
  "imageUrl": "/uploads/post_001.jpg",
  "content": ""
}
```

字段约定：

- `mode`：必填，枚举值为 `generate` / `polish`
- `imageUrl`：必填，用户准备发布的鸟类图片地址
- `content`：`polish` 模式必填，表示用户原始文案；`generate` 模式可为空字符串

返回体 `data` 字段固定为：

```json
{
  "mode": "generate",
  "content": "今天在湿地偶遇一只优雅的白鹭，安静伫立在浅水边，阳光洒在羽毛上特别好看。第一次这么近距离观察它，忍不住记录下来和大家分享。",
  "source": "deepseek"
}
```

`generate` 模式示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "mode": "generate",
    "content": "今天在湿地偶遇一只优雅的白鹭，安静伫立在浅水边，阳光洒在羽毛上特别好看。第一次这么近距离观察它，忍不住记录下来和大家分享。",
    "source": "deepseek"
  }
}
```

`polish` 模式示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "mode": "polish",
    "content": "今天在公园拍到一只特别灵动的小鸟，停在枝头时神态很安静，羽色在阳光下也很漂亮，分享给大家看看。",
    "source": "deepseek"
  }
}
```

推荐调用流程：

1. 前端先完成图片上传，拿到 `imageUrl`
2. 用户未填写文案时，调用 `POST /api/v1/posts/ai-copywriting` 且 `mode=generate`
3. 用户已填写文案时，调用 `POST /api/v1/posts/ai-copywriting` 且 `mode=polish`
4. 前端将 AI 返回的 `content` 回填到发帖输入框，确认后继续调用 `POST /api/v1/posts`

### 4.5 Posts（写接口错误码）

- `POST /posts`：`401`（未登录）
- `POST /posts/ai-copywriting`：`400/401/500`
- `PUT /posts/{postId}`：`401/403/404`
- `DELETE /posts/{postId}`：`401/403/404`
- `POST /posts/{postId}/like`：`401/404/409`（重复点赞为 `409 + 1009`）
- `POST /posts/{postId}/comments`：`401/404`

## 5. 文档维护约定

1. 任何接口字段、状态码、鉴权规则变更，先改 `docs/api.yaml`。  
2. 再同步更新本文件的“接口总览 + 前端关键契约 + 错误码约定”。  
3. 以测试为准固化契约（建议维护 `backend/tests/test_api.py` 对应断言）。

## 6. AI Copywriting V2 (2026-04)

`POST /api/v1/posts/ai-copywriting`

### 6.1 Generate Response

- `mode=generate`
- `data.content` is the final generated copy.
- `data.source` in `{deepseek_vision, deepseek, fallback}`
- `data.aiMeta` provides observability:
  - `mode`
  - `model`
  - `elapsedMs`
  - `retryCount`
  - `fallback`
  - `params.text.temperature/maxTokens`
  - `params.vision.temperature/maxTokens`

### 6.2 Polish Response

- `mode=polish`
- Returns dual variants:
  - `data.lite`
  - `data.enhanced`
  - `data.defaultVariant = "lite"`
- Backward compatibility:
  - `data.content` equals `data.lite` (frontend default render).
- `data.sources` records per-variant source.
- `data.aiMeta.variants` records per-variant observability.

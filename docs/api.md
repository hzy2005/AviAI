# AviAI API 文档（api.md）

## 1. 文档说明

本项目 API 按 OpenAPI 3.0 规范维护，完整机器可读文档见 [api.yaml](./api.yaml)。  
本文档用于快速阅读和联调，字段与状态码以 `api.yaml` 为准。

- 基础路径：`/api/v1`
- 数据格式：`application/json`
- 认证方式：`Authorization: Bearer <token>`
- 时间格式：ISO 8601（例如 `2026-03-09T10:30:00Z`）

## 2. 响应约定

所有接口统一返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

错误响应示例：

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

## 3. 接口总览

| 模块 | 方法 | 路径 | 鉴权 | 说明 |
| --- | --- | --- | --- | --- |
| Health | GET | `/health` | 否 | 服务健康检查 |
| Auth | POST | `/auth/register` | 否 | 用户注册 |
| Auth | POST | `/auth/login` | 否 | 用户登录 |
| Users | GET | `/users/me` | 是 | 获取当前用户信息 |
| Birds | POST | `/birds/recognize` | 是 | 上传图片并识别 |
| Birds | GET | `/birds/records` | 是 | 查询识别历史 |
| Posts | POST | `/posts` | 是 | 发布动态 |
| Posts | GET | `/posts` | 否 | 动态列表 |
| Posts | POST | `/posts/{postId}/like` | 是 | 点赞动态 |
| Posts | POST | `/posts/{postId}/comments` | 是 | 评论动态 |

## 4. 关键请求示例

### 4.1 登录

`POST /api/v1/auth/login`

```json
{
  "email": "bird@example.com",
  "password": "12345678"
}
```

### 4.2 识别图片

`POST /api/v1/birds/recognize`  
`Content-Type: multipart/form-data`，字段名：`image`

### 4.3 发布动态

`POST /api/v1/posts`

```json
{
  "content": "今天在湿地拍到了白鹭！",
  "imageUrl": "/uploads/post_001.jpg"
}
```

## 5. OpenAPI 使用方式

1. 导入 `docs/api.yaml` 到 Swagger Editor（https://editor.swagger.io）可直接查看接口结构。  
2. 如需本地展示，可在后端接入 Swagger UI 并加载此 yaml。  
3. 每次接口变更先更新 `api.yaml`，再同步更新本文件总览和示例。

## 6. 版本记录

- `v0.2.0`（2026-03-25）：补全 OpenAPI 3.0 规范，新增 `api.yaml`，统一组件定义与接口清单。  
- `v0.1.0`（2026-03-09）：初版接口定义，覆盖认证、识别、社区三大核心能力。  

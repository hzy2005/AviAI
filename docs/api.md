# AviAI API 文档（api.md）

## 1. 说明
- 基础路径：`/api/v1`
- 数据格式：`application/json`
- 鉴权方式：`Authorization: Bearer <token>`
- 时间格式：ISO 8601（示例：`2026-03-09T10:30:00Z`）

## 2. 通用响应结构
### 2.1 成功响应
```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

### 2.2 失败响应
```json
{
  "code": 1001,
  "message": "参数错误",
  "data": null
}
```

### 2.3 常见错误码
- 0: 成功
- 1001: 参数错误
- 1002: 未登录或 Token 无效
- 1003: 无权限
- 1004: 资源不存在
- 1005: 服务内部错误
- 1006: 上传文件不合法

## 3. 认证模块
### 3.1 用户注册
- 方法：`POST`
- 路径：`/auth/register`
- 鉴权：否

请求体：
```json
{
  "username": "birdlover",
  "email": "bird@example.com",
  "password": "12345678"
}
```

响应示例：
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "userId": 1
  }
}
```

### 3.2 用户登录
- 方法：`POST`
- 路径：`/auth/login`
- 鉴权：否

请求体：
```json
{
  "email": "bird@example.com",
  "password": "12345678"
}
```

响应示例：
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

## 4. 用户模块
### 4.1 获取当前用户信息
- 方法：`GET`
- 路径：`/users/me`
- 鉴权：是

响应示例：
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": 1,
    "username": "birdlover",
    "email": "bird@example.com",
    "avatarUrl": "",
    "createdAt": "2026-03-09T10:30:00Z"
  }
}
```

## 5. 鸟类识别模块
### 5.1 上传图片并识别
- 方法：`POST`
- 路径：`/birds/recognize`
- 鉴权：是
- Content-Type：`multipart/form-data`
- 表单字段：`image`（jpg/png，建议 <= 5MB）

响应示例：
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "recordId": 101,
    "birdName": "白鹭",
    "confidence": 0.9342,
    "imageUrl": "/uploads/20260309_xxx.jpg",
    "createdAt": "2026-03-09T10:35:00Z"
  }
}
```

### 5.2 查询识别历史
- 方法：`GET`
- 路径：`/birds/records`
- 鉴权：是
- 查询参数：
  - `page`：页码，默认 1
  - `pageSize`：每页数量，默认 10

响应示例：
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "list": [
      {
        "recordId": 101,
        "birdName": "白鹭",
        "confidence": 0.9342,
        "imageUrl": "/uploads/20260309_xxx.jpg",
        "createdAt": "2026-03-09T10:35:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 10
  }
}
```

## 6. 社区模块
### 6.1 发布动态
- 方法：`POST`
- 路径：`/posts`
- 鉴权：是

请求体：
```json
{
  "content": "今天在湿地拍到了白鹭！",
  "imageUrl": "/uploads/post_001.jpg"
}
```

### 6.2 动态列表
- 方法：`GET`
- 路径：`/posts`
- 鉴权：否
- 查询参数：`page`、`pageSize`

### 6.3 点赞动态
- 方法：`POST`
- 路径：`/posts/{postId}/like`
- 鉴权：是

### 6.4 评论动态
- 方法：`POST`
- 路径：`/posts/{postId}/comments`
- 鉴权：是

请求体：
```json
{
  "content": "拍得很清晰！"
}
```

## 7. 接口实现约定
- 所有分页接口返回 `list + total + page + pageSize`。
- 所有创建接口优先返回创建后的 `id`。
- 后端出现异常时，返回统一错误结构，不直接暴露堆栈。
- API 变更需同步更新本文件并标注版本号。

## 8. 版本记录
- v0.1（2026-03-09）：初版接口定义，覆盖认证、识别、社区三大核心能力。

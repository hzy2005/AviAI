# AviAI 后端设计文档（backend.md）

## 1. 文档目标
本文档用于说明 AviAI 项目的后端模块设计、核心职责、技术选型和开发规范，作为后端开发与联调的基础依据。

## 2. 后端职责范围
AviAI 后端主要负责以下能力：
- 用户账号管理：注册、登录、身份认证、用户信息维护。
- 鸟类识别服务：接收图片、调用 AI 识别模块、返回识别结果。
- 社区内容服务：发布动态、浏览动态、点赞评论、内容审核基础能力。
- 数据管理：用户数据、鸟类识别记录、社区内容持久化。
- 接口对外服务：为前端提供 RESTful API，并保证基本安全性与稳定性。

## 3. 技术栈
结合 README 的初步规划，后端建议采用：
- 运行环境：Node.js（LTS）
- Web 框架：Express
- 数据库：MySQL 8.x
- 鉴权机制：JWT（JSON Web Token）
- 文件存储：本地目录（开发期）/ 对象存储（生产期可扩展）
- AI 服务接入：Python 模型服务（TensorFlow 或 PyTorch）通过 HTTP 调用

## 4. 系统架构（推荐）
采用分层结构，降低耦合并便于维护：
- Router 层：路由注册、参数初步校验。
- Controller 层：请求编排、响应组织。
- Service 层：核心业务逻辑。
- Repository/DAO 层：数据库读写。
- Middleware 层：鉴权、日志、异常处理、限流（可选）。

建议目录示例：
```text
server/
  src/
    app.js
    routes/
    controllers/
    services/
    repositories/
    middlewares/
    utils/
    config/
  uploads/
  logs/
```

## 5. 核心业务流程
### 5.1 用户注册/登录
1. 前端提交账号信息。
2. 后端校验参数与唯一性。
3. 密码加密存储（如 bcrypt）。
4. 登录成功签发 JWT，返回用户基础信息。

### 5.2 鸟类识别
1. 用户上传鸟类图片。
2. 后端进行文件类型与大小校验。
3. 调用 AI 识别服务获取预测结果。
4. 将识别记录入库（用户、时间、图片路径、结果、置信度）。
5. 返回鸟类名称、置信度、描述信息（可扩展）。

### 5.3 社区互动
1. 用户发布图文动态。
2. 其他用户可浏览、点赞、评论。
3. 后端维护互动计数与时间线查询。

## 6. 数据表设计（初版）
### 6.1 users（用户表）
- id: bigint, PK
- username: varchar(50), unique
- email: varchar(100), unique
- password_hash: varchar(255)
- avatar_url: varchar(255)
- created_at: datetime
- updated_at: datetime

### 6.2 bird_records（识别记录表）
- id: bigint, PK
- user_id: bigint, FK -> users.id
- image_url: varchar(255)
- bird_name: varchar(100)
- confidence: decimal(5,4)
- raw_result: json
- created_at: datetime

### 6.3 posts（社区动态表）
- id: bigint, PK
- user_id: bigint, FK -> users.id
- content: text
- image_url: varchar(255)
- like_count: int
- comment_count: int
- created_at: datetime
- updated_at: datetime

### 6.4 comments（评论表）
- id: bigint, PK
- post_id: bigint, FK -> posts.id
- user_id: bigint, FK -> users.id
- content: text
- created_at: datetime

## 7. 安全与质量要求
- 输入校验：所有接口参数做类型、长度、格式校验。
- 鉴权拦截：除公开接口外，默认需 JWT 鉴权。
- 密码安全：使用不可逆哈希存储，不记录明文密码。
- 上传安全：限制图片 MIME、大小，避免可执行文件上传。
- 错误处理：统一错误响应结构，避免泄露内部堆栈。
- 日志规范：记录请求链路、关键操作、异常信息。

## 8. 开发规范
- API 路径统一使用 `/api/v1` 前缀。
- 响应格式统一，成功与失败结构固定（详见 api.md）。
- 数据库变更采用迁移脚本管理。
- 关键业务必须编写单元测试与接口测试。

## 9. 里程碑建议
- M1：用户模块 + 基础鉴权。
- M2：鸟类识别上传与记录闭环。
- M3：社区发布、点赞、评论能力。
- M4：性能优化与安全加固。

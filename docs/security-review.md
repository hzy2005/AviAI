# 安全审查与加固记录

## 审查范围

本次安全审查重点覆盖后端认证、鉴权、数据库访问和 AI 能力调用相关代码：

- `backend/app/core/auth.py`
- `backend/app/core/config.py`
- `backend/app/routes/auth.py`
- `backend/app/routes/users.py`
- `backend/app/routes/posts.py`
- `backend/app/routes/birds.py`
- `backend/app/routes/deps.py`
- `backend/app/services/api_service.py`
- `backend/app/db/session.py`

## 使用的 AI 审查 Prompt

```text
请对以下代码进行安全审查（OWASP Top 10 视角）：
检查内容：
1. 注入漏洞（SQL / 命令注入）
2. 失效的访问控制（未鉴权的接口）
3. 硬编码密钥或敏感信息
4. 密码是否明文存储
5. 错误信息是否暴露内部细节
对每个发现的问题：
- 说明漏洞类型和危害等级（高/中/低）
- 提供修复后的完整代码
```

## AI 审查发现的问题

### 1. 密码哈希算法过弱

- 类型：认证与凭据保护不足
- 等级：高
- 位置：`backend/app/core/auth.py`
- 问题：项目原先使用单次 `SHA-256` 进行密码哈希。虽然不是明文存储，但缺少自适应成本、随机盐和抗暴力破解能力，不符合 OWASP 对密码存储的推荐。

### 2. Logout 仅返回成功，Token 实际未失效

- 类型：失效的访问控制 / 会话管理不足
- 等级：中
- 位置：`backend/app/routes/auth.py`、`backend/app/services/api_service.py`
- 问题：原实现中 `/api/v1/auth/logout` 不要求鉴权，并且只是返回 `{success: true}`，已签发 token 仍可继续访问受保护接口。

### 3. 默认配置中存在硬编码敏感值

- 类型：敏感信息暴露
- 等级：中
- 位置：`backend/app/core/config.py`、`backend/.env.example`
- 问题：代码与模板中存在真实风格较强的默认密钥和数据库口令（如 `root:123456`、`aviai-dev-secret`），容易在开发阶段被直接沿用。

### 4. SQL 注入风险检查结果

- 类型：注入漏洞检查
- 等级：低
- 结论：当前数据库访问主要通过 SQLAlchemy ORM 与参数化查询构建，未发现明显字符串拼接 SQL 的实现。

## 已完成的修复

### 修复 1：密码哈希升级为 bcrypt，并兼容旧 SHA-256 哈希平滑迁移

- 修改文件：
  - `backend/app/core/auth.py`
  - `backend/app/services/api_service.py`
  - `backend/requirements.txt`
- 处理方式：
  - 新注册用户统一使用 `bcrypt` 哈希密码。
  - 登录时兼容历史 `SHA-256` 哈希，验证成功后自动重哈希升级为 `bcrypt`，避免旧账号无法登录。

### 修复 2：为 logout 增加鉴权并实现 token 失效

- 修改文件：
  - `backend/app/core/auth.py`
  - `backend/app/routes/auth.py`
  - `backend/app/services/api_service.py`
- 处理方式：
  - `/api/v1/auth/logout` 现在要求携带合法 Bearer Token。
  - 服务端会将当前 token 加入撤销列表，后续再使用该 token 访问受保护接口会返回 `401`。

### 修复 3：移除默认敏感配置中的真实风格凭据

- 修改文件：
  - `backend/app/core/config.py`
  - `backend/.env.example`
- 处理方式：
  - 将默认数据库连接改为本地 SQLite 安全占位。
  - 将默认 `SECRET_KEY` 改为明确的占位提示值，避免将真实风格凭据硬编码在仓库中。

## 安全检查清单

### 认证与授权

- [x] 密码存储：已改为 `bcrypt`，不再使用单次 `SHA-256`
- [x] JWT / Session：token 有过期时间；logout 后当前 token 会失效
- [x] 接口鉴权：`users/me`、`birds/*`、`posts` 写接口均通过依赖注入获取当前用户
- [x] 越权访问：鸟类记录详情/更新/删除、帖子更新/删除等操作均校验 `user_id`

### 注入防护

- [x] SQL：当前使用 SQLAlchemy ORM / 参数化查询，未发现字符串拼接 SQL
- [x] XSS：前端为微信小程序，不使用 `innerHTML`，当前场景下风险较低

### 敏感信息

- [x] API Key / 密码：DeepSeek API Key 通过环境变量读取；默认敏感配置已替换为占位值
- [x] `.env` 文件：仓库 `.gitignore` 已忽略 `.env`；项目保留 `backend/.env.example`

### 依赖安全

- [ ] 运行依赖扫描：本次 CI 选择的是密钥泄露扫描（Gitleaks），未将依赖漏洞扫描作为主选项；后续可补充 `pip-audit` / `npm audit`

## CI 自动化安全扫描

本次集成选项 A：密钥泄露扫描。

- 新增文件：`.github/workflows/security.yml`
- 扫描工具：`gitleaks/gitleaks-action@v2`
- 目标：在 `push` / `pull_request` 时自动扫描提交历史与当前仓库中的潜在密钥泄露

## 结论

本次安全审查后，项目完成了两类核心安全加固：

1. 强化密码存储与旧哈希迁移，降低凭据泄露后的撞库与暴力破解风险。
2. 修复 logout 不失效的问题，完善了 token 会话生命周期控制。

同时，项目已补充自动化密钥扫描与安全审查文档，满足本次作业“AI 辅助审查 + 至少两处修复 + CI 安全扫描”的要求。

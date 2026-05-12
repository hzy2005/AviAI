# 安全审查与加固记录

## 审查范围

本次安全审查覆盖后端认证、鉴权、数据库访问、文件上传、AI 文案调用和前端请求封装相关代码：

- `backend/app/core/auth.py`
- `backend/app/core/config.py`
- `backend/app/routes/auth.py`
- `backend/app/routes/users.py`
- `backend/app/routes/posts.py`
- `backend/app/routes/birds.py`
- `backend/app/routes/deps.py`
- `backend/app/services/api_service.py`
- `backend/app/db/session.py`
- `frontend/utils/request.js`
- `frontend/src/api/*.js`

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

### 3. 默认配置中存在硬编码敏感占位风险

- 类型：敏感信息暴露
- 等级：中
- 位置：`backend/app/core/config.py`、`backend/.env.example`
- 问题：默认配置中曾存在真实风格较强的密钥或数据库口令，容易在开发阶段被直接沿用。

### 4. 依赖版本存在已知漏洞

- 类型：易受攻击和过时组件
- 等级：中
- 位置：`backend/requirements.txt`、`frontend/package-lock.json`
- 问题：`pip-audit` 发现 `python-multipart==0.0.12`、`Pillow==10.4.0`、FastAPI 间接依赖的 `starlette==0.41.3` 存在已知 CVE；`npm audit` 发现 `brace-expansion` 中危漏洞。

### 5. SQL 注入风险检查结果

- 类型：注入风险检查
- 等级：低
- 结论：当前数据库访问主要通过 SQLAlchemy ORM 与参数化查询构建，未发现明显字符串拼接 SQL 的实现。

## 已完成的修复

### 修复 1：密码哈希升级为 bcrypt，并兼容旧 SHA-256 哈希迁移

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
  - 服务端将当前 token 加入撤销列表，后续再使用该 token 访问受保护接口会返回 `401`。

### 修复 3：移除默认敏感配置中的真实风格凭据

- 修改文件：
  - `backend/app/core/config.py`
  - `backend/.env.example`
- 处理方式：
  - 默认数据库连接使用本地 SQLite 占位。
  - 默认 `SECRET_KEY` 使用明确的占位提示，真实密钥必须通过环境变量配置。

### 修复 4：升级存在已知漏洞的依赖

- 修改文件：
  - `backend/requirements.txt`
  - `frontend/package-lock.json`
- 处理方式：
  - `fastapi`：`0.115.5` -> `0.136.1`，带入更高版本的安全版 `starlette`。
  - `python-multipart`：`0.0.12` -> `0.0.27`。
  - `Pillow`：`10.4.0` -> `12.2.0`。
  - `SQLAlchemy`：`2.0.36` -> `2.0.49`，修复 Python 3.14 环境下 ORM 类型解析兼容问题。
  - 运行 `npm audit fix` 修复前端 `brace-expansion` 中危漏洞。

## 安全检查清单

### 认证与授权

- [x] 密码存储：使用 `bcrypt` 哈希，不存明文；保留旧 SHA-256 平滑迁移逻辑。
- [x] JWT / Session：token 有过期时间；logout 后当前 token 失效。
- [x] 接口鉴权：`users/me`、`birds/*`、`posts` 写接口、AI 文案接口均通过依赖注入获取当前用户。
- [x] 越权访问：鸟类记录详情/更新/删除、帖子更新/删除均校验资源所属 `user_id`。

### 注入防护

- [x] SQL：当前使用 SQLAlchemy ORM / 参数化查询，未发现字符串拼接 SQL。
- [x] XSS：前端为微信小程序，不使用 `innerHTML`；用户内容以 WXML 文本方式渲染。

### 敏感信息

- [x] API Key / 密码：DeepSeek API Key 通过环境变量读取；默认敏感配置已替换为占位值。
- [x] `.env` 文件：仓库 `.gitignore` 已忽略 `.env`；保留 `backend/.env.example` 作为配置模板。

### 依赖安全

- [x] 前端依赖扫描：运行 `npm audit --audit-level=high`，初次发现 1 个中危 `brace-expansion`，执行 `npm audit fix` 后复扫结果为 `found 0 vulnerabilities`。
- [x] 后端依赖扫描：初扫发现 `python-multipart`、`Pillow`、`starlette` 已知漏洞；升级依赖后，使用 OSV 漏洞库复扫，结果为 `No known vulnerabilities found`。

## CI 自动化安全扫描

本次集成选项 A：密钥泄露扫描。

- 文件：`.github/workflows/security.yml`
- 工具：`gitleaks/gitleaks-action@v2`
- 触发：`push` 到 `master/develop`，以及面向 `master` 的 `pull_request`
- 目标：自动扫描提交历史和当前仓库中的潜在密钥泄露

## 命令记录

```powershell
cd frontend
npm audit --audit-level=high
npm audit fix
npm audit --audit-level=high

cd ..
python -m pip install pip-audit
python -m pip_audit -r backend\requirements.txt
python -m pip_audit --vulnerability-service osv --timeout 60 -r backend\requirements.txt --index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
python -m pytest
```

关键结果：

- `npm audit fix` 后：`found 0 vulnerabilities`
- `pip-audit` 初扫：发现 11 个漏洞，分布在 `python-multipart`、`Pillow`、`starlette`
- `pip-audit` 复扫：`No known vulnerabilities found`
- 后端测试：`78 passed, 3 warnings`

## 学习通截图清单

需人工补充以下截图：

1. Git 提交记录截图：`git log --author="YOUR_NAME" --oneline`
2. AI 审查对话截图：当前与 AI 的安全审查对话，至少 1 张
3. CI 安全扫描通过截图：GitHub Actions 中 `Security Scan` workflow 成功运行页面

## 结论

本次安全审查完成了“AI 辅助审查 + 至少两处漏洞修复 + 安全检查清单 + CI 自动化安全扫描”的核心要求。项目已完成密码存储升级、logout token 失效、敏感默认配置清理和依赖漏洞升级，并补充了自动化 gitleaks 扫描。前端 `npm audit`、后端 `pip-audit` 和后端测试均已通过；剩余需要人工完成的是学习通要求的截图材料。

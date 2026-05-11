# 安全审查贡献说明

姓名：QiuZhixiang  
学号：待补充  
日期：2026-05-12

## 我完成的工作

### AI 安全审查

- 审查了哪些文件/模块：
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
- AI 发现的主要问题：
  - 密码哈希算法过弱，原先使用单次 `SHA-256`
  - logout 接口未真正使 token 失效
  - 默认配置中存在真实风格较强的敏感值
  - 依赖扫描发现后端 `python-multipart`、`Pillow`、`starlette` 存在已知漏洞，前端 `brace-expansion` 存在中危漏洞
- 我修复了哪些问题：
  - 将密码哈希升级为 `bcrypt`
  - 增加旧 SHA-256 hash 的平滑迁移逻辑
  - 为 logout 增加鉴权与 token 撤销
  - 清理默认配置中的真实风格敏感值
  - 升级后端存在 CVE 的依赖声明，并运行 `npm audit fix` 修复前端依赖漏洞

### 安全检查清单

- [x] 密码存储：使用 `bcrypt` 哈希，不存明文
- [x] JWT / Session：token 有过期时间，logout 后当前 token 失效
- [x] 接口鉴权：需要登录的接口均有权限校验
- [x] 越权访问：用户只能操作自己的识别记录和帖子
- [x] SQL：使用 SQLAlchemy ORM / 参数化查询，无字符串拼接 SQL
- [x] XSS：微信小程序前端不使用 `innerHTML`
- [x] API Key / 密码：通过环境变量读取，`.env.example` 仅保留占位值
- [x] `.env` 文件：已加入 `.gitignore`，仓库中有 `backend/.env.example`
- [x] 依赖扫描：前端 `npm audit` 已清零；后端 `pip-audit` 已发现并修复依赖声明，复扫受本地网络超时影响，需在 CI 或稳定网络中复核

### CI 安全扫描

- 配置了哪个选项（A/B/C）：
  - 选项 A：Gitleaks 密钥泄露扫描
- 扫描结果：
  - 已新增 `.github/workflows/security.yml`
  - 在 `push` / `pull_request` 时执行 `gitleaks/gitleaks-action@v2`

### 选做完成情况

- 本次未完成选做项。

## PR 链接

- PR #待补充：https://github.com/hzy2005/AviAI/pulls

## 遇到的问题和解决

1. 问题：原 logout 只返回成功，但 token 仍然可继续访问受保护接口。  
   解决：为 logout 增加鉴权，并在服务端维护 token 撤销列表。

2. 问题：原密码哈希使用单次 `SHA-256`，安全性不足。  
   解决：升级到 `bcrypt`，并兼容旧哈希在登录时自动重哈希迁移。

3. 问题：后端依赖扫描发现 `python-multipart`、`Pillow`、`starlette` 存在已知漏洞。  
   解决：升级 `backend/requirements.txt` 中对应依赖版本；本地复扫受网络影响未完成，需要在 GitHub Actions 或稳定网络中复核。

4. 问题：前端 `npm audit` 初扫发现 `brace-expansion` 中危漏洞。  
   解决：执行 `npm audit fix`，复扫结果为 `found 0 vulnerabilities`。

## 心得体会

Vibe Coding 能很快把功能搭起来，但安全审查提醒我，功能可用不等于可以放心交付。AI 适合快速指出风险点和给出修复方向，但最终仍然要结合项目上下文判断优先级，例如先修密码存储、token 生命周期和依赖漏洞这类影响面更大的问题。安全加固不是拖慢开发，而是在减少后续返工和线上事故的概率。

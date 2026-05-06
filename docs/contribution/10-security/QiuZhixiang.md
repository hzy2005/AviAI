# 安全审查贡献说明

姓名：QiuZhixiang
学号：待补充
日期：2026-05-06

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
- AI 发现的主要问题：
  - 密码哈希算法过弱，使用单次 `SHA-256`
  - logout 接口未真正使 token 失效
  - 默认配置中存在真实风格较强的敏感值
- 我修复了哪些问题：
  - 将密码哈希升级为 `bcrypt`
  - 增加 legacy hash 平滑迁移逻辑
  - 为 logout 增加鉴权与 token 撤销
  - 清理默认配置中的真实风格敏感值

### 安全检查清单

- [x] 密码存储：使用 `bcrypt` 哈希，不存明文
- [x] JWT / Session：token 有过期时间，logout 后当前 token 失效
- [x] 接口鉴权：所有需要登录的接口都有权限校验
- [x] 越权访问：用户只能操作自己的数据
- [x] SQL：使用 ORM / 参数化查询，无字符串拼接 SQL
- [x] XSS：前端为微信小程序，不使用 `innerHTML`
- [x] API Key / 密码：通过环境变量读取，默认敏感配置已替换为占位值
- [x] `.env` 文件：已加入 `.gitignore`，仓库中有 `backend/.env.example`
- [ ] 运行依赖扫描：本次未作为主扫描项，已在安全审查文档中说明

### CI 安全扫描
- 配置了哪个选项（A/B/C）：
  - 选项 A：Gitleaks 密钥泄露扫描
- 扫描结果：
  - 已新增 `.github/workflows/security.yml`，用于在 `push` / `pull_request` 时执行自动化扫描

### 选做完成情况
- 本次未完成选做项

## PR 链接
- PR #待补充: https://github.com/hzy2005/AviAI/pulls

## 遇到的问题和解决
1. 问题：原有 logout 只返回成功，但 token 仍然可继续访问受保护接口。  
   解决：为 logout 增加鉴权，并在服务端维护 token 撤销列表。
2. 问题：原密码哈希使用单次 `SHA-256`，安全性不足。  
   解决：升级到 `bcrypt`，并兼容旧哈希在登录时自动重哈希迁移。
3. 问题：默认配置里存在真实风格较强的数据库口令和 secret。  
   解决：替换为环境变量模板占位值，并在文档中说明使用方式。

## 心得体会

在 Vibe Coding 场景下，开发效率很高，但如果只关注功能跑通，安全问题很容易被忽略。这次实践让我更明确地感受到：AI 很适合帮助我们快速发现风险点，但最后仍然需要结合项目上下文判断“哪些问题最值得先修、怎么修不会破坏现有功能”。安全加固并不是拖慢开发，而是帮我们避免后面更大的返工成本。

# 安全审查贡献说明

姓名：何周屹  
学号：2312190419  
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
  - `backend/requirements.txt`
- AI 发现的主要问题：
  - 密码哈希算法过弱，旧实现使用单次 `SHA-256`，抗暴力破解能力不足。
  - logout 接口原先没有真正使已签发 token 失效。
  - 默认配置中存在真实风格较强的敏感占位值，容易被开发环境误用。
  - 后端依赖扫描发现 `python-multipart`、`Pillow`、`starlette` 存在已知漏洞。
- 我修复了哪些问题：
  - 参与后端认证安全加固，确认密码存储升级为 `bcrypt`，并保留旧 SHA-256 哈希的平滑迁移逻辑。
  - 参与后端 token 生命周期加固，确认 logout 需要鉴权并会撤销当前 token。
  - 清理并核对后端默认配置，确保真实密钥/API Key 通过环境变量读取，`.env.example` 只保留占位值。
  - 负责后端依赖安全复核与升级，将存在漏洞或兼容问题的依赖升级到安全版本。

### 安全检查清单

- [x] 密码存储：后端使用 `bcrypt` 哈希，不存储明文密码；旧 SHA-256 哈希在登录成功后迁移。
- [x] JWT / Session：token 有过期时间；logout 后当前 token 会进入撤销列表。
- [x] 接口鉴权：`users/me`、`birds/*`、帖子写接口、AI 文案接口均校验 Bearer Token。
- [x] 越权访问：识别记录详情/更新/删除、帖子更新/删除均校验资源所属用户。
- [x] SQL：后端使用 SQLAlchemy ORM / 参数化查询，未发现字符串拼接 SQL。
- [x] XSS：项目为微信小程序前端，不使用 `innerHTML` 渲染用户内容。
- [x] API Key / 密码：DeepSeek API Key、数据库连接、secret key 均通过环境变量配置。
- [x] `.env` 文件：仓库忽略 `.env`，保留 `backend/.env.example` 作为模板。
- [x] 依赖扫描：后端 `pip-audit` 初扫发现漏洞，升级依赖后复扫结果为 `No known vulnerabilities found`。

### CI 安全扫描

- 配置了哪个选项（A/B/C）：
  - 选项 A：Gitleaks 密钥泄露扫描
- 扫描结果：
  - 已新增 `.github/workflows/security.yml`
  - 在 `push` 和 `pull_request` 时执行 `gitleaks/gitleaks-action@v2`
  - 用于自动发现提交历史和当前仓库中的潜在密钥泄露

### 选做完成情况

- 本次未完成选做项。

## PR 链接

- PR #待补充：https://github.com/hzy2005/AviAI/pull/62

## 遇到的问题和解决

1. 问题：后端依赖扫描初次发现 11 个已知漏洞，集中在 `python-multipart`、`Pillow` 和 FastAPI 间接依赖的 `starlette`。  
   解决：升级 `fastapi`、`python-multipart`、`Pillow` 等依赖版本，并复跑 `pip-audit`。

2. 问题：升级后在本地 Python 3.14 环境中运行后端测试时，`SQLAlchemy==2.0.36` 解析 `Mapped[int | None]` 类型失败。  
   解决：将 `SQLAlchemy` 升级到 `2.0.49`，再次运行后端测试通过。

3. 问题：`pip-audit` 默认访问 PyPI 漏洞服务时多次出现超时或 SSL 中断，影响复扫结果确认。  
   解决：改用 OSV 漏洞库，并指定清华 PyPI 镜像完成依赖解析，最终复扫结果为 `No known vulnerabilities found`。

4. 问题：安全审查不仅要修代码，还要保留过程证据。  
   解决：在 `docs/security-review.md` 中补充审查范围、AI 发现问题、修复说明、扫描命令、验证结果和学习通截图清单。

## 验证结果

```bash
python -m pytest
```

结果：`78 passed, 3 warnings`

```bash
python -m pip_audit --vulnerability-service osv --timeout 60 -r backend\requirements.txt --index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

结果：`No known vulnerabilities found`

## 心得体会

这次安全审查让我更清楚地认识到，后端安全不是只看业务接口是否能跑通，还要关注密码存储、token 生命周期、越权校验、依赖漏洞和配置泄露这些容易被忽略的细节。AI 能快速帮助定位风险点，但最终是否需要修、怎么修、修完是否破坏现有测试，仍然需要结合项目代码和实际运行结果判断。通过这次依赖扫描和复测，我也体会到安全加固必须留下可验证证据，只有文档、扫描结果和测试结果都闭环，才算真正完成。

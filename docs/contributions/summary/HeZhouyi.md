# 何周屹个人贡献整合文档

姓名：何周屹  
学号：2312190419  
项目名称：AviAI 鸟类识别与观鸟社区小程序  
技术栈：原生微信小程序、FastAPI、MySQL、Redis、Docker、Render、DeepSeek API  

## 一、个人总体分工

在 AviAI 项目中，我主要负责用户研究与 UI 优化、前后端架构设计、后端 API 设计与实现、数据库持久化、AI 文案辅助后端能力、后端自动化测试、CI/CD 后端增强、安全依赖复核、Docker 容器化主体实现、云部署核对和监控配置文档同步等工作。

整体来看，我的贡献重点集中在后端工程化、接口契约、数据持久化、AI 能力落地、测试质量、容器化部署和线上验收保障。

## 二、UI 设计贡献

### 1. 用户研究

在 UI 设计阶段，我通过分析产品定位，将目标用户划分为以下几类：

- 鸟类爱好者：具备一定观鸟经验，关注识别准确性与交流分享。
- 户外 / 自然观察者：在旅行或徒步场景中需要快速识别鸟类并获取基础信息。
- 摄影爱好者：希望识别照片中的鸟类，提升作品内容价值。
- 新手用户：对鸟类感兴趣但缺乏专业知识，需要低门槛、易上手的工具。

### 2. 核心用户场景

围绕产品核心功能，我梳理了三个典型使用场景：

- 即时识别：用户在户外发现鸟类，通过拍照上传进行快速识别，并查看详细信息。
- 分享交流：用户将观鸟照片发布至社区，与其他用户互动交流，获取反馈。
- 知识查询：用户在百科页搜索或浏览鸟类信息，了解习性、分布等内容。

### 3. 竞品分析

我分析了以下竞品：

- Merlin Bird ID：识别准确度高、数据权威，但偏工具属性，社区互动较弱。
- Birdty：依托智能喂鸟器使用，成本较高，鸟类数据以欧美为主，本土化不足。
- iNaturalist：社区活跃、数据专业性强，但界面复杂，对新手不友好。

由此得出的设计结论是：现有产品要么偏工具，要么偏专业社区，用户门槛较高。因此 AviAI 应强化“AI 识别 + 社区互动”的结合，并通过简化界面与操作流程提升易用性。

### 4. 页面设计优化

在团队已有设计框架基础上，我进行了整体视觉与交互优化：

- 统一视觉规范，重新整理字体与配色体系。
- 优化信息层级，使内容更加清晰易读。
- 改进交互体验，简化识别、跳转等关键操作路径。
- 增强界面可用性，降低新手理解成本。

### 5. 设计规范

配色方案包括：

- `#FFFFFF`
- `#34B663`
- `#297C57`
- `#000000`
- `#242A68`
- `#444444`
- `#8A8EB1`
- `#9E9E9E`
- `#4285F6`
- `#29BF6C`

字体方面，我在原 Rubik / Gordita 方案基础上调整为更通用的 Inter，以提升可读性和跨平台适配性。

Figma 设计链接：

```text
https://www.figma.com/design/Uv5JLhnpF13kKVHNhKPQRM/AviAI-UI?node-id=0-1&t=yDerZ4QUSjfFUZdV-1
```

### 6. 遇到的问题和解决

问题：页面设计过程中出现异常文字无法修改。  
解决：重新调整组件结构并更换字体方案，同时优化整体视觉一致性。

### 7. 心得体会

通过本次设计过程，我通过用户研究和竞品分析明确了设计方向，也对 UI 设计流程有了更系统的理解。

## 三、软件架构设计贡献

### 1. 架构设计分工

我负责：

- 前端架构设计。
- 后端架构设计。
- 系统交互流程设计。

我未作为数据库设计的主要负责人。

### 2. 前端技术选型

项目前端采用原生微信小程序框架。选择原因包括：

- 项目目标平台就是微信生态。
- 原生方案在页面渲染、API 调用和调试链路上最直接。
- 与微信开发者工具配合更稳定。
- 相比跨端框架，可以减少适配成本。
- 更适合课程项目当前的开发节奏和实现深度。

### 3. 后端技术选型

后端选择 FastAPI。选择原因包括：

- 接口开发效率高。
- 参数校验能力强。
- 自动生成接口文档方便。
- 适合“快速迭代 + 明确接口规范”的项目场景。
- 基于 Python 生态，便于后续对接智能识别服务。
- 业务服务与模型服务可以在同一技术栈下协作，降低系统集成复杂度。

### 4. 环境搭建

我完成了：

- 前端项目初始化。
- 后端项目初始化。
- 数据库连接配置。
- `AGENTS.md` 编写。

### 5. 文档编写

我编写了 `docs/architecture.md`，用于说明整体系统架构、前后端结构和系统交互流程。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/12
```

### 6. 心得体会

架构设计让我认识到，先把边界和规范写清楚，比后续反复改代码更省时间。尤其是接口字段、错误码和分页结构，前期统一之后，前后端联调会顺畅很多。

## 四、API 设计与实现贡献

### 1. API 设计

我负责：

- 用户认证 API。
- 业务资源 API。
- 查询接口设计。

### 2. 文档编写

我参与完成：

- OpenAPI 文档。
- API 使用说明。

### 3. 后端实现

我主要负责：

- API 路由定义。
- 业务逻辑处理。
- 错误处理。

### 4. 测试

我完成或参与：

- Postman / Apifox 测试集合。
- 4 组接口测试用例设计。

相关链接：

```text
https://github.com/hzy2005/AviAI/issues/20
```

### 5. 遇到的问题和解决

问题 1：前端接口调用最初分散在页面中，既有直接 `request`，也有临时拼接 URL，导致鉴权头、参数格式和错误处理不统一。  
解决：按业务拆分 `frontend/src/api/auth.js`、`users.js`、`birds.js`、`posts.js`，页面只调用业务函数；底层统一复用 `frontend/utils/request.js`。

问题 2：`/api/v1/birds/recognize` 使用 `multipart/form-data` 上传，与普通 JSON 请求链路不同，联调时容易出现字段名和响应解析不一致。  
解决：在 birds 模块独立封装 `wx.uploadFile`，固定上传字段 `image`，并对齐通用响应结构 `code/message/data`。

### 6. 心得体会

这次 API 工作让我更深入理解分层和统一约定的价值。页面层负责交互，API 层负责协议适配，后端路由层负责参数校验，服务层负责业务逻辑。统一接口前缀 `/api/v1` 和响应结构后，前后端联调成本明显下降。

## 五、后端开发贡献

### 1. API 实现

我完成了：

- 用户认证 API：注册、登录、退出、当前用户。
- Posts CRUD：创建、列表、详情、更新、删除。
- 帖子点赞功能。
- 帖子评论功能。
- Bird Records CRUD：识别创建、列表、详情、更新、删除。
- 统一错误响应结构，覆盖 401、403、404、409、500 等错误。

### 2. 数据库开发

我完成了：

- `user` 数据模型。
- `bird_record` 数据模型。
- `post` 数据模型。
- `comment` 数据模型。
- `like` 数据模型。
- SQLAlchemy ORM 配置。
- Alembic 数据库迁移脚本。

迁移脚本包括：

- `20260324_0001_create_users_table.py`
- `20260412_0002_create_bird_records_table.py`
- `20260412_0003_create_posts_comments_likes_tables.py`

### 3. 联调和持久化

我完成了：

- Auth / Birds / Posts 返回字段与状态码对齐。
- 将 auth、birds、posts、comments、likes 从 mock 形态迁移到 MySQL。
- 实现识别图片上传落盘。
- 挂载 `/uploads` 静态目录，解决前端图片 404 问题。
- 在识鸟流程中接入模型推理和兜底逻辑。
- 增加上传文件格式合法性校验。
- 补充并维护后端测试，覆盖登录、识别、记录链路以及社区 CRUD、like、comment 关键路径。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/28
```

### 4. 遇到的问题和解决

问题 1：前端加载 `/uploads/*.jpg` 返回 404。  
解决：新增上传文件落盘逻辑，并在 FastAPI 中挂载 `/uploads` 静态目录。

问题 2：联调时接口状态码与前端/文档预期不完全一致。  
解决：统一梳理 Auth、Birds、Posts 契约，补充错误码分支。

问题 3：参数校验报错格式与业务响应不统一。  
解决：新增全局异常处理，将校验异常统一映射到业务错误结构。

### 5. 心得体会

后端开发重点不只是“接口能跑”，还要保证返回契约稳定、错误码可预测、数据可持久化。通过这次迭代，我对 API 契约管理、数据库迁移和联调排障流程有了更完整的工程化认识。

## 六、AI 功能集成贡献

### 1. 功能类型

我负责社区发帖场景 AI 文案辅助的后端能力。

功能类型：

- 看图生成社区文案。
- 已有文案润色。

使用模型：

- DeepSeek 文本模型。
- DeepSeek 视觉模型。
- 本地鸟类识别与图像特征分析。

### 2. 实现内容

我完成了：

- 新增并完善 `POST /api/v1/posts/ai-copywriting`。
- 支持 `mode=generate`：用户仅上传图片时自动生成分享文案。
- 支持 `mode=polish`：用户已有文案时进行润色。
- 支持 lite / enhanced 双版本润色。
- 新增 `POST /api/v1/posts/upload-image`。
- 统一前端先上传图片再调用 AI 接口，保证模型可访问图片数据。
- 在生成链路中加入鸟类识别结果和图像视觉事实。
- 增加输出质量校验和一次重试机制。
- 增加可观测性字段：`mode`、`model`、`elapsedMs`、`retryCount`、`fallback`、`params` 等。
- 修复图片 URL 可访问性问题。
- 修复并统一中文错误提示。
- 补充 AI 接口文档说明。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/29
```

### 3. 心得体会

AI 集成最大的经验是：仅“接入模型”不等于“效果可用”。要让文案真正贴图，必须同时打通上传链路、图片可访问性、视觉上下文约束、质量校验和可观测性。

## 七、软件测试贡献

### 1. 测试文件

我完成或维护了：

- `backend/pytest.ini`
- `backend/tests/conftest.py`
- `backend/tests/test_services.py`
- `backend/tests/test_api_contract.py`
- `backend/tests/test_core_modules.py`
- `backend/tests/test_ai_copywriting_regression.py`
- `.github/workflows/test.yml`
- `codecov.yml`

### 2. 测试清单

测试覆盖内容包括：

- 正常流程：注册、登录、发帖、列表查询、AI 文案生成、鸟类识别记录。
- 异常流程：参数缺失、未登录、资源不存在、权限不足、重复点赞、非法图片后缀、数据库异常。
- Mock 隔离：MySQL、DeepSeek、torch 模型和文件存储。
- API 合约测试：`/api/v1/health`、`/api/v1/auth/login`、`/api/v1/users/me`、`/api/v1/posts`、`/api/v1/posts/ai-copywriting`、`/api/v1/birds/recognize`。
- 覆盖率配置：终端覆盖率、HTML 报告和 Codecov XML 报告。

### 3. 测试数量和覆盖率

- Service 单元测试：49 个。
- API 接口测试：10 个。
- 后端测试总数：74 个。
- 后端总覆盖率：84%。
- `app/services/api_service.py` 覆盖率：88%。
- `app/core/auth.py` 覆盖率：96%。
- `app/core/responses.py` 覆盖率：100%。

验证命令：

```bash
cd backend
pytest --cov=app --cov-report=html --cov-report=term-missing
```

验证结果：

```text
74 passed
TOTAL coverage: 84%
```

### 4. Codecov 接入

我完成了：

- 新增 GitHub Actions 工作流 `.github/workflows/test.yml`。
- 后端覆盖率上传文件：`backend/coverage.xml`。
- 后端 Codecov flag：`backend`。
- 前端覆盖率上传文件：`frontend/coverage/lcov.info`。
- 前端 Codecov flag：`frontend`。
- README 顶部添加 Backend Coverage 和 Frontend Coverage 两个徽章。

### 5. AI 辅助测试记录

使用工具：OpenAI Codex。

Prompt 示例：

```text
Step 1：整理测试夹具，提供 FastAPI TestClient、fake_user、自动清理 dependency_overrides
```

```text
Step 2：补 8 个 Service 单元测试，要求使用 unittest.mock.patch，不连真实数据库，不调用真实 DeepSeek，不加载真实 torch 模型
```

```text
Step 3：补 6 个 API 接口测试，API 测试只验证路由、响应结构、错误码，复杂业务结果通过 patch service 控制
```

```text
Step 4：跑覆盖率并补漏，总覆盖率需要超过 80%
```

AI 辅助生成了测试框架、测试用例初稿、CI 配置和文档初稿。人工负责确认真实接口、错误码、依赖关系、覆盖率结果和 CI 失败原因，并完成最终修正。

### 6. 遇到的问题和解决

问题 1：API 测试不能依赖真实 MySQL。  
解决：通过 `conftest.py` 提供 `TestClient`、`fake_user` 和 dependency override 清理机制，在 API 测试中 patch service 层返回值。

问题 2：Service 测试不能调用真实 DeepSeek 和 torch 模型。  
解决：使用 `patch.object` 替换 `_call_deepseek_chat`、`_call_deepseek_vision_chat`、`_predict_bird_from_image`、`SessionLocal` 等外部依赖。

问题 3：覆盖率最初未达到 80%。  
解决：补充 AI 文案辅助函数、图片解析、数据库异常、鉴权错误、资源不存在等分支测试，将总覆盖率提升到 84%。

问题 4：pytest 在 Windows 环境下生成临时缓存目录。  
解决：在 `pytest.ini` 中加入 `-p no:cacheprovider`，并在 `.gitignore` 中忽略 pytest 缓存、`.coverage` 和 `htmlcov/`。

问题 5：Codecov 需要区分前后端覆盖率。  
解决：在 GitHub Actions 中分别上传 backend 和 frontend 覆盖率报告，并使用两个 flag 区分。

### 7. 心得体会

测试工作让我更清楚地区分了业务正确性测试和接口契约测试。通过 Mock 隔离数据库、AI 服务和模型加载后，测试运行更稳定，也更适合作为 CI 中的自动化检查。

## 八、CI/CD 配置贡献

### 1. 工作流相关

我完成或参与：

- 编写 / 审查 `.github/workflows/ci.yml`。
- 配置 Codecov 覆盖率上传。
- 添加 README 状态徽章。

### 2. 代码适配

- 本地测试命令与 CI 保持一致。
- 后端代码通过 ruff 零警告。
- 后端 74 个用例全部通过。
- 后端总覆盖率 84%，超过要求。

### 3. 可选项

我完成了：

- 配置 Dependabot 自动更新依赖，补全后端 pip ecosystem。
- 集成 CodeRabbit AI 代码审查。
- 添加 Python 3.11 / 3.12 构建矩阵。
- 使用 act 本地验证工作流。

### 4. 具体变更

Dependabot 后端配置：

- `.github/dependabot.yml` 原本仅监控前端 npm 依赖。
- 新增 pip ecosystem，监控 `/backend` 目录。
- 每周自动扫描 `requirements.txt` 并创建 PR。

Python 多版本构建矩阵：

- 后端 job 新增 `strategy.matrix`。
- 覆盖 Python 3.11 和 3.12。
- 两个版本并行运行 ruff 和 pytest。

CodeRabbit：

- 新增 `.coderabbit.yaml`。
- 设置审查语言为中文。
- 排除 `docs/`、markdown 文件和覆盖率报告目录。

README 徽章：

- CI 徽章补充 `?branch=main`。
- 新增 CodeRabbit 审查状态徽章。

CI 运行链接：

```text
https://github.com/hzy2005/AviAI/actions/runs/25368017066
```

### 5. 遇到的问题和解决

问题 1：Dependabot 原配置只有前端 npm，后端 `requirements.txt` 无法自动更新。  
解决：追加 pip ecosystem 配置。

问题 2：CI 后端 job 原本只跑 Python 3.12，无法发现跨版本兼容性问题。  
解决：添加 Python 3.11 和 3.12 构建矩阵。

问题 3：CodeRabbit 默认英文审查，不便于团队阅读。  
解决：在 `.coderabbit.yaml` 中设置 `language: zh-CN`，并排除文档目录。

### 6. 心得体会

CI/CD 配置让我更清楚地理解了“本地能跑”和“CI 稳定跑”之间的差距。Dependabot 和 CodeRabbit 的引入也把依赖管理和代码审查从手动操作变成自动化流程。

## 九、安全审查贡献

### 1. 审查范围

我审查了：

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

### 2. AI 发现的主要问题

- 密码哈希算法过弱，旧实现使用单次 `SHA-256`。
- logout 接口原先没有真正使已签发 token 失效。
- 默认配置中存在真实风格较强的敏感占位值。
- 后端依赖 `python-multipart`、`Pillow`、`starlette` 存在已知漏洞。

### 3. 修复内容

我完成或参与：

- 确认密码存储升级为 `bcrypt`。
- 保留旧 SHA-256 哈希的平滑迁移逻辑。
- 确认 logout 需要鉴权并撤销当前 token。
- 清理并核对后端默认配置。
- 确保真实密钥/API Key 通过环境变量读取。
- 负责后端依赖安全复核与升级。
- 将存在漏洞或兼容问题的依赖升级到安全版本。

### 4. 安全检查清单

- 密码存储：后端使用 `bcrypt` 哈希，不存储明文密码。
- JWT / Session：token 有过期时间，logout 后当前 token 进入撤销列表。
- 接口鉴权：`users/me`、`birds/*`、帖子写接口、AI 文案接口均校验 Bearer Token。
- 越权访问：识别记录详情/更新/删除、帖子更新/删除均校验资源所属用户。
- SQL：后端使用 SQLAlchemy ORM / 参数化查询。
- XSS：微信小程序前端不使用 `innerHTML` 渲染用户内容。
- API Key / 密码：DeepSeek API Key、数据库连接、secret key 均通过环境变量配置。
- `.env` 文件：仓库忽略 `.env`，保留 `backend/.env.example` 作为模板。
- 依赖扫描：升级依赖后 `pip-audit` 结果为无已知漏洞。

### 5. CI 安全扫描

配置选项：Gitleaks 密钥泄露扫描。

扫描结果：

- 新增 `.github/workflows/security.yml`。
- 在 `push` 和 `pull_request` 时执行 `gitleaks/gitleaks-action@v2`。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/62
```

### 6. 遇到的问题和解决

问题 1：后端依赖扫描发现 11 个已知漏洞。  
解决：升级 `fastapi`、`python-multipart`、`Pillow` 等依赖版本，并复跑 `pip-audit`。

问题 2：升级后在本地 Python 3.14 环境中运行后端测试时，`SQLAlchemy==2.0.36` 解析 `Mapped[int | None]` 类型失败。  
解决：将 SQLAlchemy 升级到 `2.0.49`，再次运行后端测试通过。

问题 3：`pip-audit` 默认访问 PyPI 漏洞服务时多次超时或 SSL 中断。  
解决：改用 OSV 漏洞库，并指定清华 PyPI 镜像完成依赖解析。

问题 4：安全审查不仅要修代码，还要保留过程证据。  
解决：在 `docs/security-review.md` 中补充审查范围、修复说明、扫描命令、验证结果和截图清单。

### 7. 验证结果

```bash
python -m pytest
```

结果：

```text
78 passed, 3 warnings
```

```bash
python -m pip_audit --vulnerability-service osv --timeout 60 -r backend\requirements.txt --index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

结果：

```text
No known vulnerabilities found
```

### 8. 心得体会

安全审查让我认识到，后端安全不仅要看业务接口是否能跑通，还要关注密码存储、token 生命周期、越权校验、依赖漏洞和配置泄露。安全加固必须留下可验证证据，文档、扫描结果和测试结果都闭环才算真正完成。

## 十、Docker 部署贡献

### 1. Dockerfile 编写

我完成了：

- 前端 Dockerfile，多阶段构建。
- 后端 Dockerfile，多阶段构建。
- `.dockerignore` 文件。

具体内容：

- 新增 `frontend/Dockerfile`，使用 Node 阶段安装依赖、执行质量检查，并使用 Nginx runtime 镜像提供前端说明页。
- 新增 `backend/Dockerfile`，使用 Python 3.11 slim 镜像和多阶段构建安装后端依赖。
- 后端运行时使用非 root 用户 `appuser`。
- 后端容器暴露 8000 端口，并配置 `/health` 健康检查。
- 新增前后端 `.dockerignore`，排除 `.env`、`.git`、`node_modules`、缓存、覆盖率产物、构建产物和日志文件。
- 新增 `backend/requirements.docker.txt`，为 Docker 镜像构建提供更精简的依赖集合。

### 2. Compose 配置

我完成了：

- 开发环境 `compose.yaml`。
- 生产环境 `compose.prod.yaml`。
- 健康检查配置。
- 数据持久化配置。
- 生产环境 secrets 配置。

具体内容：

- `compose.yaml` 编排 `frontend`、`backend`、`db`、`redis` 服务。
- 后端服务启动时执行 `alembic upgrade head`，再启动 Uvicorn。
- MySQL 使用 `mysql:8.4`，配置 `utf8mb4` 字符集和健康检查。
- Redis 使用 `redis:7-alpine`，并配置数据卷。
- 上传目录、MySQL 数据和 Redis 数据均使用 Docker volume 持久化。
- `compose.prod.yaml` 使用 GHCR 镜像、`restart: unless-stopped`、资源限制和 Docker secrets。
- 数据库密码、root 密码和后端 `SECRET_KEY` 通过 `secrets/` 目录读取，避免写入配置文件。
- 新增 `secrets/.gitignore`，防止真实密钥文件进入仓库。

### 3. 自动化部署

我选择并完成了“构建并推送镜像到 GHCR”方案。

具体内容：

- 新增 `.github/workflows/docker.yml`。
- 使用矩阵分别构建 backend 和 frontend 镜像。
- 推送分支和手动触发时登录 GHCR 并推送镜像。
- Pull Request 场景只构建本地镜像，不推送仓库。
- 使用 Docker Buildx 和 GitHub Actions cache 加速构建。
- 使用 `docker/metadata-action` 生成分支、PR、commit sha 和 latest 标签。
- 集成 Trivy 扫描镜像漏洞，阻断 CRITICAL/HIGH 级别风险。

### 4. 镜像安全和漏洞修复

我完成了：

- 减少后端镜像中的漏洞扫描面。
- 升级前端 runtime 镜像包。
- 调整 Dockerfile 中的系统包升级和清理逻辑。
- 清理 `setuptools`、`wheel`、`pkg_resources` 等非运行时必要组件。
- 保持前后端容器使用非 root 用户运行。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/74
```

### 5. 遇到的问题和解决

问题：项目同时包含微信小程序前端和 FastAPI 后端，二者运行方式不同，不能使用单一 Dockerfile 覆盖全部场景。  
解决：分别为 `frontend` 和 `backend` 编写 Dockerfile，并在 Compose 中作为独立服务编排。

### 6. 心得体会

Docker 部署让我认识到，容器化不仅是把应用打包，还要考虑运行用户权限、健康检查、持久化、密钥管理、镜像漏洞扫描和自动化构建。

## 十一、云服务部署贡献

### 1. 平台选择与部署方案核对

我参与核对了当前项目部署方案：

- 使用平台：Render。
- 部署对象：FastAPI 后端服务。
- 数据库：云 MySQL。
- 前端验证方式：微信开发者工具运行原生微信小程序，并请求 Render 线上后端接口。

我确认原生微信小程序不适合作为普通 Web 页面直接部署，后端部署到 Render、前端在微信开发者工具中接入线上后端更符合项目实际。

### 2. 部署配置核对

我完成了：

- 核对 `render.yaml`。
- 核对后端 Docker 启动命令支持 Render 动态端口 `PORT`。
- 核对容器启动时执行 `alembic upgrade head`。
- 核对 Render 环境变量配置项。
- 核对云 MySQL 连接方式 `DATABASE_URL`。
- 核对自动部署配置。
- 核对小程序前端线上接口地址 `frontend/config/env.js`。
- 同步完善 `docs/api.md`、`docs/api.yaml`。
- 在 `backend/README.md` 中补充验收常用接口。

### 3. 环境变量配置

Render 中需要配置的主要环境变量：

- `DATABASE_URL`
- `SECRET_KEY`
- `USE_MOCK_DATA=false`
- `ACCESS_TOKEN_EXPIRE_MINUTES=10080`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL=https://api.deepseek.com/v1`
- `DEEPSEEK_MODEL=deepseek-chat`
- `DEEPSEEK_VISION_MODEL=deepseek-chat`

我重点核对了敏感信息管理方式，确认真实数据库密码、JWT 密钥和第三方 API Key 只配置在 Render 控制台，不写入仓库。

### 4. 部署验证

后端在线地址：

```text
https://aviai-backend.onrender.com
```

API 健康检查地址：

```text
https://aviai-backend.onrender.com/api/v1/health
```

平台健康检查地址：

```text
https://aviai-backend.onrender.com/health
```

验证结果：

- `/api/v1/health` 返回统一响应结构，服务状态为 `running`。
- `/health` 返回简洁健康检查结构，服务状态为 `healthy`。
- 数据库连接状态为 `connected`。

### 5. 前端接入验证

我在微信开发者工具 Network 面板中核对了小程序请求地址，确认登录接口请求发送到 Render 后端：

```text
https://aviai-backend.onrender.com/api/v1/auth/login
```

同时说明 `png`、`svg` 等请求为小程序静态资源加载，`login`、`me` 等 `xhr` 请求才是后端接口调用。

## 十二、监控配置贡献

### 1. 日志配置核对

我完成了：

- 核对结构化 JSON 日志格式。
- 核对日志级别配置。
- 核对请求日志中间件。
- 核对 Render Logs 中的日志截图方式。

具体内容：

- 核对 `backend/app/utils/logger.py` 中的 `JsonFormatter` 实现。
- 确认日志输出到标准输出。
- 确认请求日志包含 `time`、`level`、`message`、`module`、`logger`、`method`、`path`、`status_code`、`duration_ms` 和 `client` 等字段。
- 整理学习通提交时“日志输出截图”的获取方式。

### 2. 健康检查

我完成了：

- 核对 `/health` 端点。
- 核对 `/api/v1/health` 端点。
- 核对数据库连接检查逻辑。
- 同步健康检查文档。

具体内容：

- `/health` 返回适合平台健康检查和截图验收的简洁结构。
- `/api/v1/health` 返回项目统一响应结构。
- 健康检查中执行 `SELECT 1` 判断数据库连接状态。
- 在线访问验证健康检查接口，确认返回 `healthy` / `running` 和 `database: connected`。

### 3. 指标收集

我核对了：

- 请求计数。
- 响应时间。
- 错误率。
- 状态码计数。
- 活跃请求数。
- 指标接口文档同步。

具体内容：

- 核对 `backend/app/utils/metrics.py` 中的轻量级内存指标收集器。
- 确认请求中间件会统计请求数量、响应耗时、5xx 错误数和状态码分布。
- 核对 `/api/v1/metrics` 指标接口返回 `requestCount`、`errorCount`、`errorRate`、`averageResponseMs`、`activeRequests` 和 `statusCodes`。
- 在 `docs/api.md`、`docs/api.yaml` 和 `backend/README.md` 中同步补充健康检查和指标接口说明。

### 4. 文档说明

我完成了：

- 核对 `docs/monitoring.md`。
- 补充 API 文档中 `/health` 与 `/api/v1/health` 的区别。
- 补充 API 文档中 `/api/v1/metrics` 的返回结构。
- 补充后端 README 中的监控入口。
- 补充可选 Prometheus 文本格式指标接口。
- 补充可选 Sentry 错误追踪配置。
- 补充可选 UptimeRobot 服务可用性告警配置。
- 整理学习通截图清单。

### 5. 遇到的问题和解决

问题 1：`/health` 和 `/api/v1/health` 容易混淆。  
解决：明确区分根路径 `/health` 是平台健康检查，不使用统一响应包裹；`/api/v1/health` 是 API 健康检查，使用统一响应结构。

问题 2：作业要求日志输出截图，但日志不是浏览器页面直接展示。  
解决：先访问线上 `/health` 触发请求日志，再进入 Render Dashboard > `aviai-backend` > Logs 截取 JSON 日志。

问题 3：指标收集是评分项，但原后端 README 没有列出指标接口。  
解决：在 `backend/README.md` 中补充 `GET /api/v1/metrics`，并在 API 文档中补充指标字段说明。

问题 4：`/api/v1/metrics` 是 JSON 结构，不方便 Prometheus / Grafana 直接抓取。  
解决：新增根路径 `GET /metrics`，输出 Prometheus text exposition 格式，并在 `docs/monitoring.md` 中补充抓取配置示例。

问题 5：错误追踪是选做项，但不能强制依赖真实 DSN。  
解决：新增可选 Sentry 配置，仅配置 `SENTRY_DSN` 时初始化。

问题 6：服务上线后还需要知道什么时候不可用，但项目没有独立告警系统。  
解决：在 `docs/monitoring.md` 中补充 UptimeRobot 外部 HTTP(s) 监控方案。

### 6. 验证结果

线上健康检查：

```text
https://aviai-backend.onrender.com/health
```

返回结果包含：

- `status: healthy`
- `version: 0.3.0`
- `database: connected`

线上指标接口：

```text
https://aviai-backend.onrender.com/api/v1/metrics
```

返回结果包含：

- `requestCount`
- `errorCount`
- `errorRate`
- `averageResponseMs`
- `activeRequests`
- `statusCodes`

文档校验：

```bash
python -c "import pathlib, yaml; yaml.safe_load(pathlib.Path('docs/api.yaml').read_text(encoding='utf-8')); print('api.yaml parsed')"
git diff --check -- docs/api.md docs/api.yaml backend/README.md
```

校验结果：`api.yaml parsed`，无空白错误。

### 7. 心得体会

监控配置让我认识到，应用上线后还需要能被观察和验证。健康检查帮助平台判断服务是否可用，结构化日志帮助定位每次请求状态和耗时，基础指标反映请求量、错误率和响应时间。虽然当前实现是轻量级方案，但已经覆盖线上服务最基础的可观测性要求。

## 十三、整体总结

我在本项目中的贡献覆盖了架构、后端、AI、测试、CI、安全、Docker、云部署和监控等多个工程化环节。我的工作使 AviAI 从页面原型和接口设计进一步推进到可联调、可测试、可容器化、可上线和可观测的状态。

通过项目实践，我对接口契约、数据库迁移、AI 能力工程化、自动化测试、容器编排、云服务部署和运行监控有了完整认识。后续可以继续加强 AI 输出评测、真实生产级监控告警和更细粒度的性能分析。

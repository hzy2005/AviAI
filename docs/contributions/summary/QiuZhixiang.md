# 邱志翔个人贡献整合文档

姓名：邱志翔  
学号：2312190432  
项目名称：AviAI 鸟类识别与观鸟社区小程序  
技术栈：原生微信小程序、FastAPI、MySQL、Redis、Docker、Render、DeepSeek API  

## 一、个人总体分工

在 AviAI 项目中，我主要负责 UI 初版设计、数据库方案设计、前端页面开发、前端请求层封装、Mock 数据联调、AI 文案辅助前端接入、前端自动化测试、CI/CD 前端配置、安全审查与加固、Docker 配置复核、云服务部署和监控功能实现等内容。

我的工作重点集中在小程序端用户体验、接口联调、前端工程化、测试覆盖、线上部署验证和文档整理。项目中我既完成了可见页面和交互，也参与了接口契约、测试、CI、安全和部署等支撑性工作，使前端功能可以稳定演示、可测试、可上线验证。

## 二、UI 设计贡献

### 1. 页面设计

在 UI 设计阶段，我完成了 AviAI 小程序主要页面的初版设计，包括：

- 登录页和注册页设计。
- 首页设计。
- 鸟类识别详情页设计。
- 社区页设计。
- 鸟类百科页设计。
- 个人用户页设计。

这些页面覆盖了项目的核心使用链路：用户进入小程序后完成登录/注册，在首页发起识别，查看识别结果和鸟类百科信息，再通过社区进行内容发布和互动，最后在个人中心查看个人资料与历史记录。

### 2. 设计规范

我参与制定了项目初版视觉规范，主要包括配色和字体方案。

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

字体方面，初版选择 Rubik 和 Gordita，用于保证页面在视觉上具有较好的现代感和统一性。

### 3. 文档编写

我编写并整理了设计说明文档和交互说明，说明主要页面的视觉结构、页面功能、用户操作路径和交互关系。

Figma 设计链接：

```text
https://www.figma.com/design/Uv5JLhnpF13kKVHNhKPQRM/AviAI-UI?node-id=0-1&t=yDerZ4QUSjfFUZdV-1
```

### 4. 遇到的问题和解决

问题：页面设计时出现了不必要的文字，而且无法直接修改。  
解决：重新调整 UI 设计，替换字体方案，修复异常文字问题，并保证页面视觉一致性。

### 5. 心得体会

通过 UI 设计阶段，我认识到前端页面设计是项目实现的重要前置步骤。只有先把页面结构、配色、布局和交互路径梳理清楚，后续代码实现时才不会反复返工。

## 三、架构与数据库设计贡献

### 1. 架构设计分工

在软件架构设计阶段，我主要负责数据库设计相关内容。

完成情况：

- 前端架构设计：未作为主要负责人。
- 后端架构设计：未作为主要负责人。
- 数据库设计：负责。
- 系统交互流程设计：未作为主要负责人。

### 2. 数据库技术选型

我选择 MySQL 作为观鸟社区应用的主要数据库，原因包括：

- 项目涉及用户注册、帖子发布、点赞、评论、鸟类识别记录等关系型数据。
- 用户名和邮箱需要唯一约束。
- 同一用户不能重复点赞同一篇帖子。
- 删除帖子时需要处理关联图片、评论、点赞等数据。
- MySQL 的 InnoDB 引擎支持事务和外键约束，适合保证数据一致性。
- 用户、帖子、评论、鸟类物种等实体之间关系清晰，适合关系型数据库建模。
- MySQL 生态成熟，文档和工具丰富，后续可对接云数据库服务。
- 性能优化可以通过索引、读写分离、Redis 缓存等常规方式逐步扩展。

整体判断是：对当前课程项目和业务规模来说，MySQL 足够稳定、成熟、成本低，没有必要引入更复杂的数据库方案。

### 3. 环境和文档工作

我主要负责编写 `docs/database.md`，整理数据库实体、字段设计和数据关系。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/12
```

### 4. 心得体会

架构设计让我更深刻地理解了“合适比先进更重要”。观鸟社区的数据关系清晰，查询模式相对固定，用 MySQL 加 Redis 的经典组合就能满足需求。过度设计不仅不会提升项目质量，反而会增加开发和运维成本。

## 四、API 设计与实现贡献

### 1. 前端 API 层实现

在 API 设计与实现阶段，我主要负责前端访问层和部分后端实现、测试工作。

完成内容包括：

- HTTP 客户端配置。
- API 调用函数封装。
- Mock 数据配置。
- API 路由定义。
- 业务逻辑处理。
- 错误处理。
- 后端单元测试。

我新增并维护了 `frontend/src/api/` 目录，按照业务模块拆分接口调用逻辑，使页面不再直接拼接 URL 或直接写请求细节。

### 2. 请求封装

我继续复用 `frontend/utils/request.js` 作为统一底层请求层，集中处理：

- 请求基础路径。
- token 注入。
- 请求超时。
- 响应结构解析。
- 错误提示。
- Mock 优先分发逻辑。

这样可以让页面层只关注业务交互，避免每个页面重复写请求基础逻辑。

### 3. Mock 数据配置

为了保证前端在后端接口尚未稳定时也能独立演示，我补充了 Mock 处理文件和示例 `db.json`，用于模拟登录、用户信息、识别记录、社区帖子等数据。

### 4. 遇到的问题和解决

问题 1：小程序端既要满足课程要求的 `frontend/src/api/` 目录，又要保持项目已有请求封装统一。  
解决：新增 `frontend/src/api/` 模块目录，同时继续复用 `frontend/utils/request.js` 作为统一底层请求层。

问题 2：前端联调时缺少稳定的演示数据。  
解决：补充 Mock 处理文件和示例 `db.json`，便于截图、演示和前端独立调试。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/18
```

### 5. 心得体会

这次工作让我认识到，前端 API 层不仅是“发请求”，更重要的是统一认证、错误处理、接口组织方式和响应结构。访问层整理好之后，页面逻辑会更干净，后续联调和功能扩展也更轻松。

## 五、前端开发贡献

### 1. 页面开发

我负责完成了多个小程序页面开发：

- 登录页面。
- 注册页面。
- 首页/列表页面。
- 详情页面。
- 个人中心。
- 社区页面。
- 个人设置页。
- 识别记录页。
- 鸟类百科页。

这些页面基本覆盖了 AviAI 小程序的主要用户路径。

### 2. 组件和模块封装

我完成或维护了以下关键模块：

- `frontend/utils/request.js`：统一封装网络请求、错误处理和 Mock 优先分发逻辑。
- `frontend/src/api/`：按业务模块拆分认证、用户、鸟类识别、社区帖子等 API 调用层。
- `frontend/utils/mock-api.js`：提供前端联调用的虚假后端数据、登录态校验和本地持久化能力。

### 3. API 对接

我对接了以下后端接口：

- `/auth/register`
- `/auth/login`
- `/auth/logout`
- `/users/me`
- `/birds/recognize`
- `/birds/records`
- `/posts`
- `/posts/{postId}`
- `/posts/{postId}/like`
- `/posts/{postId}/comments`

同时处理了页面中的加载状态、错误提示、登录态判断和请求失败回退。

### 4. 遇到的问题和解决

问题 1：前端页面较多，如果登录、鉴权、请求错误提示分散写在各页面中，后续维护会混乱。  
解决：抽离 `request.js` 和 `src/api/` 访问层，把请求发送、返回结构处理、token 注入和错误提示收口到公共模块中。

问题 2：后端接口在开发阶段尚未完全稳定，前端联调和页面演示容易被阻塞。  
解决：补充 `mock-api.js`，用 Mock 数据模拟登录、用户资料、识别记录和社区帖子，并支持本地持久化。

问题 3：个人中心、登录注册页和设置页视觉风格不统一。  
解决：统一这些页面的样式，调整输入框、按钮、导航栏和页面布局。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/25
```

### 5. 心得体会

这次前端开发让我更清楚地理解了页面实现和接口联调之间的关系。除了把界面做出来，更重要的是把请求层、Mock 数据、状态管理和错误处理整理清楚，这样页面功能才稳定、可维护。

## 六、AI 功能集成贡献

### 1. 功能类型

我负责社区发帖 AI 文案辅助功能的前端调用和交互接入。

功能包括：

- 图片生成文案。
- 已有文案润色。

使用模型：

- DeepSeek API。

### 2. 实现内容

我完成的具体工作包括：

- 按项目接口规范补充社区 AI 文案辅助接口文档。
- 新增并说明 `POST /api/v1/posts/ai-copywriting`。
- 明确 `generate` 和 `polish` 两种调用模式。
- 在社区页 Create Post 弹窗中新增 AI 按钮。
- 根据输入框内容动态切换按钮文案状态。
- 接入前端帖子 API 调用层。
- 完成 AI 文案生成/润色请求发送与返回结果回填。
- 补充前端 Mock 能力，保证后端接口未完成时也能演示 AI 文案辅助流程。
- 处理未上传图片、请求失败、生成中状态提示等基础异常场景。

### 3. 调用模式

`generate` 模式：用户仅上传图片时，自动生成社区分享文案。  
`polish` 模式：用户已经输入原始文案时，对已有文案进行润色。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/31
```

### 4. 心得体会

AI 接口不只是把模型接入项目，还要先把前端交互场景想清楚。什么时候生成、什么时候润色、失败时怎么提示、结果如何回填，都需要和接口契约同步设计。

## 七、软件测试贡献

### 1. 测试文件

我完成了前端测试相关文件：

- `frontend/src/__tests__/page-interactions.test.js`
- `frontend/src/__tests__/api-mock.test.js`
- `frontend/src/__tests__/coverage-boost.test.js`
- `frontend/src/__tests__/helpers/test-utils.js`

### 2. 测试范围

测试覆盖内容包括：

- 登录流程。
- 注册流程。
- 社区发帖。
- AI 文案辅助。
- 识别结果发布。
- 请求失败回退。
- Mock 数据契约。
- 页面交互状态。
- API 请求封装。

### 3. 测试数量和覆盖率

测试清单：

- 组件渲染 / 交互测试：27 个。
- Mock API / 请求 / 工具测试：20 个。
- AI 生成 + 人工修改的测试数量：47 个。

覆盖率结果：

- 运行命令：`npm test`
- 覆盖率命令：`npm test -- --coverage`
- 本地终端总行覆盖率：94.56%。
- 分支覆盖率：76.60%。
- 函数覆盖率：90.29%。
- 业务代码覆盖率：92.77%。

重点覆盖模块：

- `pages/login`
- `pages/register`
- `pages/community`
- `pages/recognize`
- `src/api`
- `utils/request`
- `utils/mock-api`

### 4. AI 辅助测试记录

使用工具：OpenAI Codex。

Prompt 示例：

```text
严格参照我的API文档，请帮我完成前端部分的作业任务，不要修改后端的文件。
```

补充 Prompt：

```text
我的前端测试文件不是应该放在 frontend/src/__tests__/ 目录下吗，帮我修改移动一下。
```

```text
这里我使用你 codex 来作为 AI 辅助测试，请帮我实现前端部分任务，不要修改后端。
```

AI 先基于 `docs/api.md` 生成小程序页面交互测试和 Mock API 测试，我再人工确认目录、补充覆盖率脚本、LCOV 产物、README/Codecov 配置，并针对低覆盖模块继续补测。

### 5. 遇到的问题和解决

问题 1：项目是原生微信小程序，不能直接照搬 React Testing Library。  
解决：改用 Node 原生测试运行器，手动 mock `wx`、`Page`、`setTimeout`，对页面逻辑和 API 层做可重复执行的自动化测试。

问题 2：社区页面同时包含搜索、发帖、AI 文案、图片上传、编辑和删除等多种状态，直接测试耦合较高。  
解决：拆成页面交互测试、API/Mock 测试和覆盖率提升测试三组文件。

问题 3：课程要求严格参照 API 文档，小程序前端又存在本地 Mock 联调逻辑。  
解决：测试时统一以 `docs/api.md` 约定的 `code / message / data` 结构、`/api/v1` 路径和关键字段为断言基准。

问题 4：终端覆盖率和 Codecov 覆盖率口径不完全一致。  
解决：在贡献说明中同时记录 Node 终端总覆盖率和 `coverage-summary.json` 的业务代码覆盖率。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/38
```

### 6. 心得体会

前端测试不只是“点页面有没有反应”，而是要把输入校验、接口调用、异常提示、状态切换这些细节固定下来。通过测试，我把社区发帖、AI 文案辅助、请求失败回退这些真实风险点固化成可重复执行的断言。

## 八、CI/CD 配置贡献

### 1. 工作流相关

我参与完成：

- 编写 / 审查 `.github/workflows/ci.yml`。
- 配置 Codecov 覆盖率上传，区分 backend / frontend flag。
- 添加 README 状态徽章。

### 2. 代码适配

- 本地测试命令与 CI 保持一致。
- 前端代码通过 ESLint 检查。
- 前端覆盖率报告生成 `frontend/coverage/lcov.info`。

### 3. 可选项

- 配置 Dependabot 自动更新依赖。
- 未集成 CodeRabbit AI 代码审查。
- 未使用 act 本地验证工作流。

### 4. 遇到的问题和解决

问题 1：原有前端测试命令依赖 PowerShell 脚本，不适合直接放到 Ubuntu CI。  
解决：改为 Node 脚本入口，统一本地和 CI 的测试行为。

问题 2：仓库里原先是拆分工作流，且前端 coverage 里包含占位上传逻辑。  
解决：合并为单个 `ci.yml`，保留真实测试产物上传。

问题 3：README 徽章仍指向旧分支和旧工作流。  
解决：统一切换为 `main` 分支和 `ci.yml` 工作流地址。

问题 4：前端依赖升级如果完全手动维护，容易遗漏。  
解决：新增 `.github/dependabot.yml`，让 GitHub 定期检查 `frontend/` 下的 npm 依赖更新。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/40
```

CI 运行链接：

```text
https://github.com/hzy2005/AviAI/actions/runs/25363464378
```

### 5. 心得体会

这次主要收获是把“本地能跑”进一步整理成“CI 也能稳定跑”。把测试入口、覆盖率产物和工作流路径统一之后，后续联调和验收会顺畅很多。

## 九、安全审查贡献

### 1. 审查范围

我审查了以下文件或模块：

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

### 2. AI 发现的主要问题

- 密码哈希算法过弱，原先使用单次 `SHA-256`。
- logout 接口未真正使 token 失效。
- 默认配置中存在真实风格较强的敏感值。
- 后端依赖 `python-multipart`、`Pillow`、`starlette` 存在已知漏洞。
- 前端依赖 `brace-expansion` 存在中危漏洞。

### 3. 修复内容

我修复或参与修复了：

- 将密码哈希升级为 `bcrypt`。
- 增加旧 SHA-256 hash 的平滑迁移逻辑。
- 为 logout 增加鉴权与 token 撤销。
- 清理默认配置中的真实风格敏感值。
- 升级后端存在 CVE 的依赖声明。
- 运行 `npm audit fix` 修复前端依赖漏洞。

### 4. 安全检查清单

- 密码存储：使用 `bcrypt` 哈希，不存明文。
- JWT / Session：token 有过期时间，logout 后当前 token 失效。
- 接口鉴权：需要登录的接口均有权限校验。
- 越权访问：用户只能操作自己的识别记录和帖子。
- SQL：使用 SQLAlchemy ORM / 参数化查询，无字符串拼接 SQL。
- XSS：微信小程序前端不使用 `innerHTML`。
- API Key / 密码：通过环境变量读取，`.env.example` 仅保留占位值。
- `.env` 文件：已加入 `.gitignore`。
- 依赖扫描：前端 `npm audit` 清零，后端 `pip-audit` 修复后无已知漏洞。

### 5. CI 安全扫描

配置选项：Gitleaks 密钥泄露扫描。

扫描结果：

- 新增 `.github/workflows/security.yml`。
- 在 `push` / `pull_request` 时执行 `gitleaks/gitleaks-action@v2`。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/60
```

### 6. 遇到的问题和解决

问题 1：原 logout 只返回成功，但 token 仍然可继续访问受保护接口。  
解决：为 logout 增加鉴权，并在服务端维护 token 撤销列表。

问题 2：原密码哈希使用单次 `SHA-256`，安全性不足。  
解决：升级到 `bcrypt`，并兼容旧哈希在登录时自动重哈希迁移。

问题 3：后端依赖扫描发现多个已知漏洞，升级后又暴露 SQLAlchemy 类型解析兼容问题。  
解决：升级相关依赖，并将 SQLAlchemy 升级到 `2.0.49`，复跑 `pip-audit` 和后端测试。

问题 4：前端 `npm audit` 初扫发现 `brace-expansion` 中危漏洞。  
解决：执行 `npm audit fix`，复扫结果为 `found 0 vulnerabilities`。

### 7. 心得体会

安全审查提醒我，功能可用不等于可以放心交付。AI 能快速指出风险点和修复方向，但最终仍然要结合项目上下文判断优先级，例如密码存储、token 生命周期和依赖漏洞这类问题应优先处理。

## 十、Docker 部署贡献

### 1. 个人分工

在 Docker 容器化部署中，我主要负责代码检查、配置复核和贡献文档补充。前后端 Dockerfile、Compose 配置和 GitHub Actions 自动化构建扫描主要由何周屹完成。

### 2. Dockerfile 检查

我检查了：

- 前端 Dockerfile 是否使用多阶段构建。
- 后端 Dockerfile 是否使用 Python slim 镜像、多阶段构建和非 root 用户。
- 后端容器是否暴露 8000 端口。
- 后端是否配置健康检查。
- `.dockerignore` 是否排除 `.env`、`.git`、`node_modules`、测试覆盖率产物等文件。

### 3. Compose 配置检查

我检查了：

- `compose.yaml` 是否包含 `frontend`、`backend`、`db`、`redis` 服务。
- 后端是否依赖 MySQL 健康检查。
- 后端启动时是否执行数据库迁移。
- `compose.prod.yaml` 是否使用 GHCR 镜像、持久化卷和 Docker secrets。
- MySQL、Redis、上传目录是否配置持久化卷。

### 4. 自动化部署检查

我检查了：

- `.github/workflows/docker.yml` 的触发分支和构建矩阵。
- 前后端镜像是否分别构建。
- Trivy 漏洞扫描是否覆盖 CRITICAL/HIGH 级别问题。
- 个人贡献说明是否准确反映实际分工。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/74
```

### 5. 遇到的问题和解决

问题 1：我在本次任务中没有直接实现 Dockerfile 和 Compose 主体配置，个人贡献容易与主要实现者混淆。  
解决：在贡献说明中明确标注自己的工作范围，说明我主要负责代码检查、配置复核和文档补充。

问题 2：Docker 配置涉及开发环境、生产环境、镜像构建、安全扫描和密钥管理，检查范围分散。  
解决：按照作业要求拆分为 Dockerfile、Compose、自动化部署、安全配置和截图证明逐项复核。

问题 3：前端是微信小程序，不是普通 Web 前端。  
解决：确认前端容器提供说明页，后端容器作为主要可访问服务，文档中说明小程序需通过微信开发者工具运行。

### 6. 心得体会

容器化不只是写 Dockerfile，还要考虑镜像体积、非 root 用户、环境变量、密钥管理、服务依赖、健康检查和自动化扫描。通过检查代码和补充文档，我更清楚地理解了项目从本地开发到容器化运行所需要的完整配置链路。

## 十一、云服务部署贡献

### 1. 平台选择

我负责 Render 部署方案的主要落地工作。

部署信息：

- 使用平台：Render。
- 部署对象：FastAPI 后端服务。
- 数据库：云 MySQL。
- 前端验证方式：微信开发者工具运行原生微信小程序，并请求 Render 后端接口。

选择 Render 的原因：

- Render 支持 Docker Web Service，适合当前项目已有的 `backend/Dockerfile`。
- Render 可以连接 GitHub 仓库，实现推送后自动部署。
- Render 自动提供 HTTPS 域名，便于小程序前端请求线上后端。

### 2. 部署配置

我完成了：

- 编写 Render 部署配置文件 `render.yaml`。
- 调整后端 Docker 启动命令，支持 Render 动态端口 `PORT`。
- 配置容器启动时执行 `alembic upgrade head`。
- 在 Render 控制台配置环境变量。
- 配置云 MySQL，并通过 `DATABASE_URL` 连接后端服务。
- 连接 GitHub 仓库并开启 Auto Deploy。
- 使用 `feature/QiuZhixiang-cloud` 分支完成首次部署验证。
- PR 合并到 `develop` 后，将 Render 部署分支切换为 `develop`。
- 新增部署说明文档 `docs/deployment.md`。
- 修改 `frontend/config/env.js`，使小程序请求 Render 后端。

### 3. 环境变量配置

Render 中配置的主要环境变量：

- `DATABASE_URL`
- `SECRET_KEY`
- `USE_MOCK_DATA=false`
- `ACCESS_TOKEN_EXPIRE_MINUTES=10080`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL=https://api.deepseek.com/v1`
- `DEEPSEEK_MODEL=deepseek-chat`
- `DEEPSEEK_VISION_MODEL=deepseek-chat`

敏感信息只配置在 Render 控制台，没有写入仓库。

### 4. 部署验证

后端在线地址：

```text
https://aviai-backend.onrender.com
```

健康检查地址：

```text
https://aviai-backend.onrender.com/api/v1/health
```

FastAPI 文档地址：

```text
https://aviai-backend.onrender.com/docs
```

健康检查结果显示：

- 后端服务状态：`running`。
- 数据库连接状态：`connected`。

### 5. 前端接入验证

前端为原生微信小程序，不适合像普通 Web 项目一样部署到 Vercel。当前前端采用微信开发者工具运行，并将后端接口地址配置为：

```text
https://aviai-backend.onrender.com
```

在微信开发者工具 Network 面板中，已验证登录等接口请求访问 Render 后端，例如：

```text
https://aviai-backend.onrender.com/api/v1/auth/login
```

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/81
```

### 6. 遇到的问题和解决

问题 1：Render 会通过 `PORT` 环境变量分配运行端口，原 Dockerfile 固定使用 8000 端口。  
解决：将 Uvicorn 启动命令改为支持 `${PORT:-8000}`。

问题 2：云端首次启动时数据库表结构可能还不存在。  
解决：容器启动时先执行 `alembic upgrade head`，再启动 FastAPI 服务。

问题 3：前端是原生微信小程序，不能像普通 Web 前端一样直接部署到 Vercel。  
解决：后端部署到 Render，前端在微信开发者工具中运行，并将请求地址切换到 Render 后端。

问题 4：当前使用的小程序测试号无法上传体验版。  
解决：使用微信开发者工具本地运行进行验证，并保留 Network 请求截图。

### 7. 心得体会

云服务部署让我完整体验了从本地开发到线上访问的流程。后端部署不只需要服务能启动，还需要处理动态端口、环境变量、数据库连接、数据库迁移和健康检查。原生微信小程序与普通 Web 前端的部署方式不同，也需要结合微信开发者工具和小程序平台实际限制设计验证方式。

## 十二、监控配置贡献

### 1. 日志配置

我完成了：

- 结构化日志格式。
- 日志级别配置。
- 请求日志中间件。

具体内容：

- 新增 `backend/app/utils/logger.py`。
- 实现 `JsonFormatter`，将日志输出为 JSON 格式。
- 在请求日志中记录请求方法、路径、状态码、响应时间和客户端地址。
- 将日志输出到标准输出，方便在本地终端、Docker 日志和 Render Logs 中查看。

### 2. 健康检查

我完成了：

- 新增 `/health` 端点。
- 保留 `/api/v1/health` 端点。
- 增加数据库连接检查逻辑。

具体内容：

- `/health` 返回适合平台健康检查和截图验收的简洁结构。
- `/api/v1/health` 继续使用项目统一响应结构。
- 健康检查中执行 `SELECT 1` 判断数据库连接状态。

### 3. 指标收集

我完成了：

- 请求计数。
- 响应时间。
- 错误率。
- 状态码计数。
- 活跃请求数。

具体内容：

- 新增 `backend/app/utils/metrics.py`。
- 使用进程内存记录基础指标。
- 新增 `/api/v1/metrics` 指标接口。
- 指标返回 `requestCount`、`errorCount`、`errorRate`、`averageResponseMs`、`activeRequests` 和 `statusCodes`。

### 4. 文档说明

我完成了：

- 新增 `docs/monitoring.md`。
- 补充日志字段说明。
- 补充健康检查端点说明。
- 补充指标接口说明。
- 补充学习通截图清单。

相关 PR：

```text
https://github.com/hzy2005/AviAI/pull/79
```

### 5. 遇到的问题和解决

问题 1：项目原来已有 `/api/v1/health`，但作业要求明确演示 `/health` 端点。  
解决：保留 `/api/v1/health` 不破坏原有 API 契约，同时新增 `/health` 返回简洁健康检查结构。

问题 2：基础指标需要统计请求计数、响应时间和错误率，但项目暂时没有引入 Prometheus 等监控依赖。  
解决：实现轻量级内存指标收集器，满足课程作业基础监控要求，后续可扩展为 Prometheus/Grafana。

问题 3：日志需要方便在 Render 中截图查看。  
解决：将结构化 JSON 日志输出到标准输出，Render Logs 可以直接展示请求日志。

### 6. 验证结果

本地验证命令：

```bash
pytest backend/tests -c backend/pytest.ini
```

需要截图验证的地址：

```text
https://aviai-backend.onrender.com/health
https://aviai-backend.onrender.com/api/v1/metrics
```

日志截图位置：

```text
Render Dashboard > aviai-backend > Logs
```

### 7. 心得体会

监控配置让我理解到，应用上线后不能只关注“能不能访问”，还需要知道服务是否健康、请求是否变慢、错误是否增加。结构化日志、健康检查和基础指标可以让运行情况变得可观察。

## 十三、整体总结

从 UI 设计、前端开发、接口联调、AI 功能、测试、CI、安全、Docker、云部署到监控配置，我参与了项目从原型到可演示、可测试、可部署的完整过程。最大的收获是理解了项目交付不是单点功能堆叠，而是页面、接口、数据、测试、部署、安全和监控之间的协同。

后续如果继续完善项目，我会重点提升前端异常场景体验、真实接口联调稳定性、AI 文案效果评估和线上监控能力，让 AviAI 更接近一个完整可维护的小程序产品。

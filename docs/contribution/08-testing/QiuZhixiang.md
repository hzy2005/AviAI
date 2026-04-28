# 软件测试贡献说明

姓名：邱志翔  学号：2312190432  角色：前端  日期：2026-04-25

## 完成的测试工作

### 测试文件

- `frontend/src/__tests__/page-interactions.test.js`
- `frontend/src/__tests__/api-mock.test.js`
- `frontend/src/__tests__/coverage-boost.test.js`
- `frontend/src/__tests__/helpers/test-utils.js`

### 测试清单

- [x] 组件渲染 / 交互测试（27 个）
- [x] Mock API / 请求 / 工具测试（20 个，含失败场景）
- [x] 覆盖登录、注册、社区发帖、AI 文案辅助、识别结果发布等核心前端流程

### 覆盖率

- 运行命令：`npm test`
- 覆盖率命令：`npm test -- --coverage`
- 核心模块覆盖率：`92.77%`（基于 `frontend/coverage/coverage-summary.json` 的业务代码统计）
- 重点覆盖模块：`pages/login`、`pages/register`、`pages/community`、`pages/recognize`、`src/api`、`utils/request`、`utils/mock-api`

### AI 辅助

- 使用工具：OpenAI Codex
- Prompt 示例：`严格参照我的API文档，请帮我完成前端部分的作业任务，不要修改后端的文件。`
- 补充 Prompt：`我的前端测试文件不是应该放在 frontend/src/__tests__/ 目录下吗，帮我修改移动一下。`
- 补充 Prompt：`这里我使用你 codex 来作为 AI 辅助测试，请帮我实现前端部分任务，不要修改后端。`
- AI 生成 + 人工修改的测试数量：47 个
- 修改过程说明：
  - 先由 AI 基于 `docs/api.md` 生成小程序页面交互测试和 Mock API 测试
  - 再人工确认测试目录改为 `frontend/src/__tests__/`
  - 最后补充覆盖率脚本、LCOV 产物、README / Codecov 配置，并继续针对低覆盖模块补测到 80% 以上

## PR 链接

- PR #X: https://github.com/hzy2005/AviAI/pull/38

## 遇到的问题和解决

1. 问题：项目是原生微信小程序，不能直接照搬 React Testing Library。
解决：改用 Node 原生测试运行器，手动 mock `wx`、`Page`、`setTimeout`，对页面逻辑和 API 层做可重复执行的自动化测试。

2. 问题：社区页面同时包含搜索、发帖、AI 文案、图片上传等多种状态，直接测试耦合较高。
解决：拆成“页面交互测试”和“API / Mock 测试”两组文件，把上传、AI 文案、鉴权、成功失败提示分别断言。

3. 问题：课程要求严格参照 API 文档，小程序前端又存在本地 mock 联调逻辑。
解决：测试时统一以 `docs/api.md` 约定的 `code / message / data` 结构、`/api/v1` 路径和关键字段为断言基准，同时验证 mock 数据契约一致性。

## 心得体会

这次测试作业让我更清楚地意识到，前端测试不只是“点页面有没有反应”，而是要把输入校验、接口调用、异常提示、状态切换这些细节都固定下来。对微信小程序项目来说，只要把 `wx` 能力和页面对象抽象好，一样可以建立比较稳定的自动化测试体系。这样以后改登录、发帖、AI 文案辅助这些功能时，就能更快发现回归问题，联调也会更有底气。

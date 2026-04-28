# 软件测试贡献说明

姓名：何周屹  
学号：2312190419  
角色：后端测试  
日期：2026-04-28

## 完成的测试工作

### 测试文件
- `backend/pytest.ini`
- `backend/tests/conftest.py`
- `backend/tests/test_services.py`
- `backend/tests/test_api_contract.py`
- `backend/tests/test_core_modules.py`
- `backend/tests/test_ai_copywriting_regression.py`
- `.github/workflows/test.yml`
- `codecov.yml`

### 测试清单
- [x] 正常情况测试：覆盖注册、登录、发帖、列表查询、AI 文案生成、鸟类识别记录等正常流程。
- [x] 边界 / 异常情况测试：覆盖参数缺失、未登录、资源不存在、权限不足、重复点赞、非法图片后缀、数据库异常等分支。
- [x] Mock 使用：使用 `unittest.mock.patch`、`patch.object`、`MagicMock` 隔离 MySQL、DeepSeek、torch 模型和文件存储等外部依赖。
- [x] API 合约测试：覆盖 `/api/v1/health`、`/api/v1/auth/login`、`/api/v1/users/me`、`/api/v1/posts`、`/api/v1/posts/ai-copywriting`、`/api/v1/birds/recognize` 等接口。
- [x] 覆盖率配置：使用 `pytest-cov` 生成终端覆盖率、HTML 报告和 Codecov 上传所需的 XML 报告。

### 测试数量
- Service 单元测试：`backend/tests/test_services.py`，共 49 个测试用例，满足“单元测试（含 Mock）不少于 8 个”的要求。
- API 接口测试：`backend/tests/test_api_contract.py`，共 10 个测试用例，满足“API 接口测试不少于 6 个，且包含异常情况”的要求。
- 后端测试总数：74 个测试用例。

### 覆盖率
- 后端总覆盖率：84%
- `app/services/api_service.py`：88%
- `app/core/auth.py`：96%
- `app/core/responses.py`：100%

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

### Codecov 接入
- 新增 GitHub Actions 工作流：`.github/workflows/test.yml`
- 后端覆盖率上传文件：`backend/coverage.xml`
- 后端 Codecov flag：`backend`
- 前端覆盖率上传文件：`frontend/coverage/lcov.info`
- 前端 Codecov flag：`frontend`
- README 顶部已添加 `Backend Coverage` 和 `Frontend Coverage` 两个徽章。

## AI 辅助测试记录

### 使用的 AI 工具
- OpenAI Codex

### 使用过的 Prompt
- “Step 1：整理测试夹具，提供 FastAPI TestClient、fake_user、自动清理 dependency_overrides”
- “Step 2：补 8 个 Service 单元测试，要求使用 unittest.mock.patch，不连真实数据库，不调用真实 DeepSeek，不加载真实 torch 模型”
- “Step 3：补 6 个 API 接口测试，API 测试只验证路由、响应结构、错误码，复杂业务结果通过 patch service 控制”
- “Step 4：跑覆盖率并补漏，总覆盖率需要超过 80%”

### AI 辅助生成的内容
- 生成 `backend/tests/conftest.py` 中的共享测试夹具，包括 `client`、`fake_user` 和依赖覆盖清理逻辑。
- 生成 `backend/tests/test_services.py` 中的 Service 单元测试，覆盖注册、登录、上传图片、AI 文案、点赞、评论、鸟类识别记录等业务函数。
- 生成 `backend/tests/test_api_contract.py` 中的 API 合约测试，覆盖正常返回、参数校验失败、未登录、资源不存在等接口场景。
- 生成 `backend/tests/test_core_modules.py` 中的核心模块测试，覆盖鉴权、统一响应、schemas 参数校验等内容。
- 生成 GitHub Actions 和 Codecov 配置，上传 `backend/coverage.xml` 和 `frontend/coverage/lcov.info`，并使用 `backend`、`frontend` 两个 flag 区分覆盖率。

### 人工审查和修改过程
- 根据项目实际 API 前缀 `/api/v1`、统一响应结构 `code/message/data`，检查并调整 API 测试断言。
- 根据真实 service 函数返回的错误码，修正测试中的期望值，例如 `1001` 参数错误、`1002` 未登录、`1004` 资源不存在、`1009` 冲突。
- 检查所有 Mock 目标，确保测试不会连接真实 MySQL、不会请求真实 DeepSeek、不会加载真实 torch 模型。
- 运行 `pytest --cov=app --cov-report=html --cov-report=term-missing`，根据覆盖率缺口继续补充低成本分支测试。
- 发现 CI 环境缺少 `httpx` 后，人工确认 FastAPI `TestClient` 依赖该包，并补充到 `backend/requirements.txt`。
- 发现主分支是 `master` 而不是 `main` 后，修正 README 徽章和 GitHub Actions 触发分支。
- 对 Codecov 页面结果进行核对，确认 backend flag 覆盖率为 83.81%，满足后端覆盖率要求。

### AI 生成与人工修改的比例说明
- AI 辅助生成了测试框架、测试用例初稿、CI 配置和文档初稿。
- 人工负责确认项目真实接口、错误码、依赖关系、覆盖率结果和 CI 失败原因，并完成最终修正。
- 最终提交前均通过本地测试和 GitHub Actions 检查。

## PR 链接
- 当前分支：`feature/HeZhouyi-backend-test`
- PR 链接：待提交到 GitHub 后填写

## 遇到的问题和解决

1. 问题：API 测试不能依赖真实 MySQL。  
   解决：通过 `conftest.py` 统一提供 `TestClient`、`fake_user` 和 dependency override 清理机制，在 API 测试中 patch service 层返回值。

2. 问题：Service 测试不能调用真实 DeepSeek 和 torch 模型。  
   解决：使用 `patch.object` 替换 `_call_deepseek_chat`、`_call_deepseek_vision_chat`、`_predict_bird_from_image`、`SessionLocal` 等外部依赖。

3. 问题：覆盖率最初未达到 80%。  
   解决：补充 AI 文案辅助函数、图片解析、数据库异常、鉴权错误、资源不存在等低成本分支测试，将总覆盖率提升到 84%。

4. 问题：pytest 在 Windows 环境下生成 `pytest-cache-files-*` 临时目录。  
   解决：在 `pytest.ini` 中加入 `-p no:cacheprovider`，并在 `.gitignore` 中忽略 pytest 缓存、`.coverage` 和 `htmlcov/`。

5. 问题：Codecov 需要区分前后端覆盖率。  
   解决：在 GitHub Actions 中分别上传 backend 和 frontend 覆盖率报告，并使用 `backend`、`frontend` 两个 flag，在 README 顶部分别展示徽章。

## 心得体会

这次测试工作让我更清楚地区分了“业务正确性测试”和“接口契约测试”。Service 层测试重点验证业务分支和错误码，API 测试重点验证路由、参数校验和响应结构。通过 Mock 隔离数据库、AI 服务和模型加载后，测试运行更稳定，也更适合作为 CI 中的自动化检查。覆盖率提升过程中，我也意识到覆盖率不是简单堆测试数量，而是要优先补关键模块、异常分支和外部依赖失败场景。

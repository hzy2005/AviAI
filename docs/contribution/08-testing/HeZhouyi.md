# 软件测试贡献说明

姓名：何周易  
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

## AI 辅助
- 使用工具：Codex
- Prompt 示例：
  - “帮我完成 Step 2：整理测试夹具”
  - “Step 3：补 8 个 Service 单元测试”
  - “Step 4：补 6 个 API 接口测试”
  - “测试覆盖率需要超80%”
  - “额外接 GitHub Actions + Codecov”
- AI 生成测试数量：主要辅助生成 Service、API、Core 模块测试和 Codecov CI 配置。
- 人工修改内容：根据项目实际接口、错误码、Mock 目标、Windows 本地权限问题和覆盖率结果，对测试断言、fixture、CI 上传路径和 README 徽章进行调整。

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

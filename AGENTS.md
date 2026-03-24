# 项目规则

## 技术栈
- 前端：原生微信小程序（JavaScript + WXML + WXSS）
- 后端：FastAPI + Python
- 数据层：MySQL + Redis + 对象存储（图片文件）
- 运行方式：前端在微信开发者工具运行，后端使用 Uvicorn 启动

## 目录结构
- `frontend/` - 小程序前端工程
- `frontend/pages/` - 页面目录
- `frontend/utils/` - 通用工具与请求封装
- `frontend/config/` - 环境配置
- `backend/app/` - 后端应用代码
- `backend/requirements.txt` - 后端依赖
- `docs/` - 架构、接口、数据库等文档

## 代码规范
- 前端页面按“页面逻辑 + 视图 + 样式”拆分（`.js/.wxml/.wxss`）
- 网络请求统一走 `frontend/utils/request.js`
- 后端接口统一使用 `/api/v1` 前缀
- API 响应统一为 `code / message / data` 结构
- 新增接口时同步更新 `docs/api.md`

## 禁止事项
- 不要在多个页面重复写请求基础逻辑
- 不要把敏感信息（密钥、密码）写入仓库
- 不要跳过参数校验直接入库
- 不要绕过鉴权访问受保护接口
- 不要改动文档与接口实现但不做同步说明

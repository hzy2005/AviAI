# AviAI

[![CI](https://github.com/hzy2005/AviAI/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/hzy2005/AviAI/actions)
[![Backend Coverage](https://codecov.io/gh/hzy2005/AviAI/branch/master/graph/badge.svg?flag=backend)](https://codecov.io/gh/hzy2005/AviAI)
[![Frontend Coverage](https://codecov.io/gh/hzy2005/AviAI/branch/master/graph/badge.svg?flag=frontend)](https://codecov.io/gh/hzy2005/AviAI)
[![CodeRabbit](https://img.shields.io/coderabbit/prs/github/hzy2005/AviAI)](https://coderabbit.ai/gh/hzy2005/AviAI)

## 团队成员

| 姓名   | 学号       | 分工         |
| 邱志翔 | 2312190432 | 前端开发     |
| 何周屹 | 2312190432 | 后端开发     |


## 项目简介

**AviAI** 是一款面向鸟类爱好者和自然观察者开发的智能鸟类识别与交流平台。用户可以通过上传或拍摄鸟类图片，利用人工智能技术快速识别鸟类种类，并获取相关的鸟类信息。

除了识别功能外，AviAI 还提供了一个专门为爱鸟人士打造的社群模块。用户可以在平台中分享观鸟记录、发布图片、交流经验，并与其他鸟类爱好者互动交流。

本项目旨在通过人工智能技术降低鸟类识别的门槛，同时构建一个开放、友好的鸟类爱好者社区，让更多人参与到鸟类观察与   生态保护中。

## 技术栈（初步规划）

* 前端：微信小程序原始框架
* 后端：Node.js / Express
* 数据库：MySQL
* AI模型：TensorFlow / PyTorch（用于鸟类图像识别）

## Figma链接
- https://www.figma.com/design/Uv5JLhnpF13kKVHNhKPQRM/AviAI-UI?node-id=0-1&t=yDerZ4QUSjfFUZdV-1

## 测试与覆盖率

- 前端测试命令：`cd frontend && npm test`
- 前端覆盖率命令：`cd frontend && npm test -- --coverage`
- 前端覆盖率产物：
  - `frontend/coverage/term-report.txt`
  - `frontend/coverage/lcov.info`
  - `frontend/coverage/coverage-summary.json`

## Codecov 说明

- GitHub Actions 工作流文件：`.github/workflows/ci.yml`
- 上传前请在 GitHub 仓库 Secrets 中配置 `CODECOV_TOKEN`
- 当前 README 顶部已预留前后端两个独立 flag 徽章：
  - `backend`
  - `frontend`

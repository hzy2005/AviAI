const { auth, birds, posts, users } = require("../../src/api/index");
const { request } = require("../../utils/request");

function stringifyPayload(payload) {
  return JSON.stringify(payload, null, 2);
}

function formatError(error) {
  if (!error) {
    return "unknown error";
  }

  if (error.message) {
    return error.message;
  }

  if (error.errMsg) {
    return error.errMsg;
  }

  if (error.statusCode || error.code) {
    return stringifyPayload(error);
  }

  return String(error);
}

function chooseImageFile() {
  return new Promise((resolve, reject) => {
    wx.chooseMedia({
      count: 1,
      mediaType: ["image"],
      sourceType: ["album", "camera"],
      success: resolve,
      fail: reject
    });
  });
}

Page({
  data: {
    email: "bird@example.com",
    password: "12345678",
    keyword: "",
    postContent: "今天在湿地拍到了白鹭，正在做 API 联调演示。",
    loadingText: "",
    hasToken: false,
    healthText: "点击按钮检查后端接口状态",
    currentUser: null,
    posts: [],
    records: [],
    recognizeResult: null,
    lastResultTitle: "最近一次接口响应",
    lastResultText: "这里会显示接口返回结果，方便截图和联调。"
  },

  onLoad() {
    this.syncTokenState();
  },

  onShow() {
    this.syncTokenState();
    this.onFetchPosts();
    if (this.data.hasToken) {
      this.bootstrapAuthedData();
    }
  },

  syncTokenState() {
    const token = wx.getStorageSync("accessToken");
    this.setData({
      hasToken: Boolean(token)
    });
  },

  setLoading(loadingText = "") {
    this.setData({ loadingText });
  },

  clearLoading() {
    this.setData({ loadingText: "" });
  },

  updateLastResult(title, payload) {
    this.setData({
      lastResultTitle: title,
      lastResultText: typeof payload === "string" ? payload : stringifyPayload(payload)
    });
  },

  ensureLogin() {
    if (this.data.hasToken) {
      return true;
    }

    wx.showToast({
      title: "请先登录",
      icon: "none"
    });
    return false;
  },

  async bootstrapAuthedData() {
    try {
      await Promise.all([
        this.onFetchUser({ silent: true }),
        this.onFetchRecords({ silent: true })
      ]);
    } catch (error) {
      this.updateLastResult("自动刷新失败", formatError(error));
    }
  },

  onEmailInput(event) {
    this.setData({ email: event.detail.value });
  },

  onPasswordInput(event) {
    this.setData({ password: event.detail.value });
  },

  onKeywordInput(event) {
    this.setData({ keyword: event.detail.value });
  },

  onPostContentInput(event) {
    this.setData({ postContent: event.detail.value });
  },

  async onCheckHealth() {
    this.setLoading("正在检查服务状态");
    try {
      const response = await request({
        url: "/api/v1/health"
      });
      this.setData({
        healthText: stringifyPayload(response)
      });
      this.updateLastResult("健康检查成功", response);
    } catch (error) {
      const message = formatError(error);
      this.setData({
        healthText: message
      });
      this.updateLastResult("健康检查失败", message);
    } finally {
      this.clearLoading();
    }
  },

  async onQuickLogin() {
    this.setLoading("正在登录");
    try {
      const response = await auth.login({
        email: this.data.email,
        password: this.data.password
      });
      this.syncTokenState();
      this.updateLastResult("登录成功", response);
      await this.bootstrapAuthedData();
      await this.onFetchPosts({ silent: true });
    } catch (error) {
      this.updateLastResult("登录失败", formatError(error));
    } finally {
      this.clearLoading();
    }
  },

  async onLogout() {
    this.setLoading("正在登出");
    try {
      const response = await auth.logout();
      this.syncTokenState();
      this.setData({
        currentUser: null,
        records: [],
        recognizeResult: null
      });
      this.updateLastResult("登出成功", response);
    } catch (error) {
      this.updateLastResult("登出失败", formatError(error));
    } finally {
      this.clearLoading();
    }
  },

  async onFetchUser(options = {}) {
    if (!this.ensureLogin()) {
      return;
    }

    if (!options.silent) {
      this.setLoading("正在获取用户信息");
    }

    try {
      const response = await users.getCurrentUser();
      this.setData({
        currentUser: response.data
      });
      this.updateLastResult("获取当前用户成功", response);
      return response;
    } catch (error) {
      this.updateLastResult("获取当前用户失败", formatError(error));
      throw error;
    } finally {
      if (!options.silent) {
        this.clearLoading();
      }
    }
  },

  async onFetchPosts(options = {}) {
    if (!options.silent) {
      this.setLoading("正在获取帖子列表");
    }

    try {
      const response = await posts.list({
        page: 1,
        pageSize: 10,
        keyword: this.data.keyword
      });
      this.setData({
        posts: response.data.list || []
      });
      this.updateLastResult("获取帖子列表成功", response);
      return response;
    } catch (error) {
      this.updateLastResult("获取帖子列表失败", formatError(error));
      throw error;
    } finally {
      if (!options.silent) {
        this.clearLoading();
      }
    }
  },

  async onFetchRecords(options = {}) {
    if (!this.ensureLogin()) {
      return;
    }

    if (!options.silent) {
      this.setLoading("正在获取识别记录");
    }

    try {
      const response = await birds.getRecords({
        page: 1,
        pageSize: 10
      });
      this.setData({
        records: response.data.list || []
      });
      this.updateLastResult("获取识别记录成功", response);
      return response;
    } catch (error) {
      this.updateLastResult("获取识别记录失败", formatError(error));
      throw error;
    } finally {
      if (!options.silent) {
        this.clearLoading();
      }
    }
  },

  async onCreatePost() {
    if (!this.ensureLogin()) {
      return;
    }

    this.setLoading("正在发布帖子");
    try {
      const response = await posts.create({
        content: this.data.postContent,
        imageUrl: "/uploads/demo_post.jpg"
      });
      this.updateLastResult("发布帖子成功", response);
      await this.onFetchPosts({ silent: true });
    } catch (error) {
      this.updateLastResult("发布帖子失败", formatError(error));
    } finally {
      this.clearLoading();
    }
  },

  async onLikePost(event) {
    if (!this.ensureLogin()) {
      return;
    }

    const { id } = event.currentTarget.dataset;
    this.setLoading("正在点赞帖子");
    try {
      const response = await posts.like(id);
      this.updateLastResult("点赞成功", response);
      await this.onFetchPosts({ silent: true });
    } catch (error) {
      this.updateLastResult("点赞失败", formatError(error));
    } finally {
      this.clearLoading();
    }
  },

  async onViewPostDetail(event) {
    const { id } = event.currentTarget.dataset;
    this.setLoading("正在获取帖子详情");
    try {
      const response = await posts.detail(id);
      this.updateLastResult("帖子详情", response);
    } catch (error) {
      this.updateLastResult("获取帖子详情失败", formatError(error));
    } finally {
      this.clearLoading();
    }
  },

  async onUpdatePost(event) {
    if (!this.ensureLogin()) {
      return;
    }

    const { id, content } = event.currentTarget.dataset;
    this.setLoading("正在更新帖子");
    try {
      const response = await posts.update(id, {
        content: `${content}（已更新）`,
        imageUrl: "/uploads/demo_post_updated.jpg"
      });
      this.updateLastResult("更新帖子成功", response);
      await this.onFetchPosts({ silent: true });
    } catch (error) {
      this.updateLastResult("更新帖子失败", formatError(error));
    } finally {
      this.clearLoading();
    }
  },

  async onDeletePost(event) {
    if (!this.ensureLogin()) {
      return;
    }

    const { id } = event.currentTarget.dataset;
    this.setLoading("正在删除帖子");
    try {
      const response = await posts.remove(id);
      this.updateLastResult("删除帖子成功", response);
      await this.onFetchPosts({ silent: true });
    } catch (error) {
      this.updateLastResult("删除帖子失败", formatError(error));
    } finally {
      this.clearLoading();
    }
  },

  async onChooseImageRecognize() {
    if (!this.ensureLogin()) {
      return;
    }

    try {
      const chooseResult = await chooseImageFile();
      const file = chooseResult.tempFiles[0];
      this.setLoading("正在上传图片识别");
      const response = await birds.recognize(file.tempFilePath);
      this.setData({
        recognizeResult: response.data
      });
      this.updateLastResult("图片识别成功", response);
      await this.onFetchRecords({ silent: true });
    } catch (error) {
      if (error && error.errMsg && error.errMsg.indexOf("cancel") >= 0) {
        return;
      }
      this.updateLastResult("图片识别失败", formatError(error));
    } finally {
      this.clearLoading();
    }
  }
});

const { posts } = require("../../src/api/index");
const { requireAuth } = require("../../utils/auth");
const { formatDateTime, toPercent, toFullImageUrl } = require("../../utils/format");

Page({
  data: {
    result: null,
    loadingPost: false
  },

  onShow() {
    const data = wx.getStorageSync("latestRecognizeResult");
    if (!data) {
      this.setData({ result: null });
      return;
    }

    this.setData({
      result: {
        ...data,
        createdAtText: formatDateTime(data.createdAt || Date.now()),
        confidenceText: toPercent(data.confidence),
        fullImageUrl: toFullImageUrl(data.imageUrl)
      }
    });
  },

  onPreviewImage() {
    const src = this.data.result && (this.data.result.localTempPath || this.data.result.fullImageUrl);
    if (!src) {
      return;
    }
    wx.previewImage({ urls: [src], current: src });
  },

  async onPostToCommunity() {
    if (!requireAuth()) {
      return;
    }

    if (!this.data.result) {
      return;
    }

    const { result } = this.data;
    const content = `今天识别到：${result.birdName}（置信度 ${result.confidenceText}）`;

    this.setData({ loadingPost: true });
    try {
      await posts.create({
        content,
        imageUrl: result.imageUrl || null
      });
      wx.showToast({ title: "已发布到社区", icon: "success" });
    } catch (error) {
      wx.showToast({ title: error.message || "发布失败", icon: "none" });
    } finally {
      this.setData({ loadingPost: false });
    }
  }
});

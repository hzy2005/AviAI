const { birds } = require("../../src/api/index");
const { requireAuth } = require("../../utils/auth");
const { formatDateTime, toPercent, toFullImageUrl } = require("../../utils/format");

Page({
  data: {
    list: [],
    page: 1,
    pageSize: 10,
    noMore: false,
    loading: false
  },

  onShow() {
    if (!requireAuth()) {
      return;
    }
    this.resetAndLoad();
  },

  onPullDownRefresh() {
    this.resetAndLoad().finally(() => wx.stopPullDownRefresh());
  },

  onReachBottom() {
    if (!this.data.noMore && !this.data.loading) {
      this.loadMore();
    }
  },

  async resetAndLoad() {
    this.setData({ list: [], page: 1, noMore: false });
    await this.loadMore();
  },

  async loadMore() {
    this.setData({ loading: true });
    try {
      const res = await birds.getRecords({
        page: this.data.page,
        pageSize: this.data.pageSize
      });

      const current = this.data.list;
      const incoming = (res.data.list || []).map((item) => ({
        ...item,
        confidenceText: toPercent(item.confidence),
        createdAtText: formatDateTime(item.createdAt),
        fullImageUrl: toFullImageUrl(item.imageUrl)
      }));

      const merged = [...current, ...incoming];
      const total = res.data.total || 0;

      this.setData({
        list: merged,
        page: this.data.page + 1,
        noMore: merged.length >= total
      });
    } catch (error) {
      wx.showToast({ title: error.message || "加载失败", icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  },

  onOpenResult(event) {
    const index = Number(event.currentTarget.dataset.index);
    const record = this.data.list[index];
    if (!record) {
      return;
    }
    wx.setStorageSync("latestRecognizeResult", record);
    wx.setStorageSync(`birdDetailRecord-${record.recordId}`, record);
    wx.navigateTo({ url: `/pages/bird-detail/bird-detail?mode=record&recordId=${record.recordId}` });
  }
});

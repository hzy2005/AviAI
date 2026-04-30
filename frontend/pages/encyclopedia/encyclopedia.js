const { birds } = require("../../src/api/index");
const { BIRD_KNOWLEDGE } = require("../../utils/bird-knowledge");
const { requireAuth, hasToken } = require("../../utils/auth");
const { formatDateTime, toPercent, toFullImageUrl } = require("../../utils/format");

const RECORD_IMAGE_MAP_KEY = "recordImageMap";

const BIRD_THUMBS = [
  "/static/view/loginbird.png",
  "/static/view/Cover.jpg",
  "/static/view/index-back.jpg"
];

function withBirdThumb(item, index) {
  return {
    ...item,
    thumbUrl: item.thumbUrl || BIRD_THUMBS[index % BIRD_THUMBS.length]
  };
}

function buildRecordThumb(item) {
  const url = String(item.imageUrl || "");
  if (!url) {
    return "";
  }

  // Prefer original captured/local image when available.
  if (/^wxfile:\/\//.test(url) || /^file:\/\//.test(url) || /^https?:\/\//.test(url) || /^\/static\//.test(url)) {
    return url;
  }

  if (url.startsWith("/")) {
    return toFullImageUrl(url);
  }

  return url;
}

Page({
  data: {
    activeTab: "kind",
    keyword: "",
    hasAuthToken: false,
    defaultThumb: BIRD_THUMBS[0],
    kindList: BIRD_KNOWLEDGE.map(withBirdThumb),
    filteredKindList: BIRD_KNOWLEDGE.map(withBirdThumb),
    recordList: [],
    loadingRecords: false
  },

  onShow() {
    const tokenState = hasToken();
    const initialTab = wx.getStorageSync("encyclopediaInitialTab");
    const nextTab = initialTab === "records" || initialTab === "kind" ? initialTab : this.data.activeTab;
    if (initialTab) {
      wx.removeStorageSync("encyclopediaInitialTab");
    }

    this.setData({
      activeTab: nextTab,
      hasAuthToken: tokenState,
      filteredKindList: this.getFilteredKindList(this.data.keyword)
    });

    if (nextTab === "records" && tokenState) {
      this.loadRecords();
    }
  },

  onKeywordInput(event) {
    const keyword = event.detail.value.trim();
    this.setData({
      keyword,
      filteredKindList: this.getFilteredKindList(keyword)
    });
  },

  onSwitchTab(event) {
    const tab = event.currentTarget.dataset.tab;
    this.setData({ activeTab: tab });

    if (tab === "records" && hasToken()) {
      this.loadRecords();
    }
  },

  getFilteredKindList(rawKeyword) {
    const keyword = String(rawKeyword || "").toLowerCase();
    if (!keyword) {
      return this.data.kindList;
    }

    return this.data.kindList.filter((item) => {
      const text = `${item.commonName} ${item.chineseName} ${item.scientificName}`.toLowerCase();
      return text.includes(keyword);
    });
  },

  async loadRecords() {
    this.setData({ loadingRecords: true });
    try {
      // Strictly follow API docs: GET /api/v1/birds/records
      const res = await birds.getRecords({ page: 1, pageSize: 20 });
      const recordImageMap = wx.getStorageSync(RECORD_IMAGE_MAP_KEY) || {};
      const previousThumbMap = (this.data.recordList || []).reduce((acc, item) => {
        const key = String(item.recordId || "");
        if (key && item.thumbUrl) {
          acc[key] = item.thumbUrl;
        }
        return acc;
      }, {});
      const list = (res.data.list || []).map((item) => ({
        ...item,
        confidenceText: toPercent(item.confidence),
        createdAtText: formatDateTime(item.createdAt),
        thumbUrl:
          recordImageMap[String(item.recordId)] ||
          previousThumbMap[String(item.recordId)] ||
          buildRecordThumb(item)
      }));
      this.setData({ recordList: list });
    } catch (error) {
      wx.showToast({ title: error.message || "Load records failed", icon: "none" });
    } finally {
      this.setData({ loadingRecords: false });
    }
  },

  onOpenBird(event) {
    const id = event.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/bird-detail/bird-detail?id=${id}` });
  },

  onOpenRecord(event) {
    if (!requireAuth({ redirect: true })) {
      return;
    }

    const index = Number(event.currentTarget.dataset.index);
    const record = this.data.recordList[index];
    if (!record) {
      return;
    }
    wx.setStorageSync("latestRecognizeResult", record);
    wx.setStorageSync(`birdDetailRecord-${record.recordId}`, record);
    wx.navigateTo({ url: `/pages/bird-detail/bird-detail?mode=record&recordId=${record.recordId}` });
  },

  onGoLogin() {
    wx.navigateTo({ url: "/pages/login/login" });
  }
});

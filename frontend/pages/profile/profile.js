const { users, birds, auth } = require("../../src/api/index");
const { requireAuth, hasToken } = require("../../utils/auth");
const { formatDateTime, toPercent, toFullImageUrl } = require("../../utils/format");

const DEFAULT_COVER = "/static/design/personal-account.jpg";
const DEFAULT_AVATAR = "/static/icons/icon-user.png";
const COVER_STORAGE_KEY = "profileCoverImage";

function chooseSingleImage() {
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

function getCardSize(index) {
  const mod = index % 4;
  if (mod === 0) return "large";
  if (mod === 1) return "medium";
  if (mod === 2) return "tall";
  return "medium";
}

function getRecordTitle(item) {
  const name = String(item.birdName || "").trim();
  if (!name) return "Bird Recording";
  return name.length > 20 ? `${name.slice(0, 20)}...` : name;
}

function mergeProfileWithDraft(profile = {}, draft = {}) {
  return {
    ...profile,
    username: draft.username || profile.username || "",
    email: draft.email || profile.email || "",
    avatarUrl: draft.avatarUrl || profile.avatarUrl || ""
  };
}

Page({
  data: {
    hasToken: false,
    profile: null,
    coverImage: DEFAULT_COVER,
    avatarUrl: DEFAULT_AVATAR,
    totalRecords: 0,
    records: [],
    leftFeed: [],
    rightFeed: [],
    loadingRecords: false
  },

  onShow() {
    const loggedIn = hasToken();
    if (!loggedIn) {
      wx.reLaunch({ url: "/pages/login/login" });
      return;
    }

    const cachedProfile = wx.getStorageSync("userProfile") || null;
    const draft = wx.getStorageSync("profileDraft") || {};
    const mergedCached = loggedIn && cachedProfile
      ? mergeProfileWithDraft(cachedProfile, draft)
      : null;
    this.setData({
      hasToken: loggedIn,
      coverImage: wx.getStorageSync(COVER_STORAGE_KEY) || DEFAULT_COVER,
      profile: loggedIn ? (mergedCached || null) : null,
      avatarUrl: loggedIn
        ? (toFullImageUrl(mergedCached && mergedCached.avatarUrl) || DEFAULT_AVATAR)
        : DEFAULT_AVATAR
    });

    this.loadProfile();
    this.loadRecords();
  },

  async loadProfile() {
    const draft = wx.getStorageSync("profileDraft") || {};
    try {
      const res = await users.getCurrentUser();
      const merged = mergeProfileWithDraft(res.data || {}, draft);
      wx.setStorageSync("userProfile", merged);
      this.setData({
        profile: merged,
        avatarUrl: toFullImageUrl(merged.avatarUrl) || DEFAULT_AVATAR
      });
    } catch (error) {
      const fallback = wx.getStorageSync("userProfile");
      if (fallback) {
        const merged = mergeProfileWithDraft(fallback, draft);
        this.setData({
          profile: merged,
          avatarUrl: toFullImageUrl(merged.avatarUrl) || DEFAULT_AVATAR
        });
        return;
      }
      if (error && Number(error.code) === 1002) {
        wx.removeStorageSync("accessToken");
        wx.reLaunch({ url: "/pages/login/login" });
        return;
      }
      wx.showToast({ title: error.message || "Load profile failed", icon: "none" });
    }
  },

  buildMasonry(records) {
    const leftFeed = [];
    const rightFeed = [];

    records.forEach((item, index) => {
      const card = {
        ...item,
        sizeClass: getCardSize(index)
      };

      if (index % 2 === 0) {
        leftFeed.push(card);
      } else {
        rightFeed.push(card);
      }
    });

    return { leftFeed, rightFeed };
  },

  async loadRecords() {
    this.setData({ loadingRecords: true });
    try {
      // Strictly follow API docs: GET /api/v1/birds/records
      const res = await birds.getRecords({ page: 1, pageSize: 40 });
      const list = (res.data.list || []).map((item) => ({
        ...item,
        fullImageUrl: toFullImageUrl(item.imageUrl),
        confidenceText: toPercent(item.confidence),
        createdAtText: formatDateTime(item.createdAt),
        displayTitle: getRecordTitle(item)
      }));

      const { leftFeed, rightFeed } = this.buildMasonry(list);
      this.setData({
        totalRecords: Number(res.data.total || list.length),
        records: list,
        leftFeed,
        rightFeed
      });
    } catch (error) {
      wx.showToast({ title: error.message || "Load records failed", icon: "none" });
    } finally {
      this.setData({ loadingRecords: false });
    }
  },

  async onChangeCover() {
    if (!requireAuth()) {
      return;
    }

    try {
      const chooseRes = await chooseSingleImage();
      const file = chooseRes.tempFiles && chooseRes.tempFiles[0];
      if (!file || !file.tempFilePath) {
        return;
      }

      wx.setStorageSync(COVER_STORAGE_KEY, file.tempFilePath);
      this.setData({ coverImage: file.tempFilePath });
    } catch (error) {
      if (error && error.errMsg && error.errMsg.includes("cancel")) {
        return;
      }
      wx.showToast({ title: "Cover update failed", icon: "none" });
    }
  },

  onGoEdit() {
    if (!requireAuth()) {
      return;
    }
    wx.navigateTo({ url: "/pages/profile-edit/profile-edit" });
  },

  onGoLogin() {
    wx.navigateTo({ url: "/pages/login/login" });
  },

  onOpenRecord(event) {
    if (!requireAuth()) {
      return;
    }

    const recordId = Number(event.currentTarget.dataset.id || 0);
    const record = this.data.records.find((item) => Number(item.recordId) === recordId);
    if (!record) {
      return;
    }

    wx.setStorageSync("latestRecognizeResult", record);
    wx.setStorageSync(`birdDetailRecord-${record.recordId}`, record);
    wx.navigateTo({ url: `/pages/bird-detail/bird-detail?mode=record&recordId=${record.recordId}` });
  },

  onPreviewImage(event) {
    const src = event.currentTarget.dataset.src;
    if (!src) {
      return;
    }

    wx.previewImage({ urls: [src], current: src });
  },

  async onLogout() {
    if (!requireAuth({ redirect: false })) {
      return;
    }

    try {
      await auth.logout();
      wx.showToast({ title: "Logged out", icon: "success" });
      wx.reLaunch({ url: "/pages/login/login" });
    } catch (error) {
      wx.showToast({ title: error.message || "Logout failed", icon: "none" });
    }
  }
});

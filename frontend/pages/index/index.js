const { birds, users } = require("../../src/api/index");
const { requireAuth } = require("../../utils/auth");
const { toPercent, toFullImageUrl } = require("../../utils/format");
const { findBirdByName } = require("../../utils/bird-knowledge");

const RECORD_IMAGE_MAP_KEY = "recordImageMap";

function chooseImageFromCamera() {
  return new Promise((resolve, reject) => {
    wx.chooseMedia({
      count: 1,
      mediaType: ["image"],
      sourceType: ["camera"],
      success: resolve,
      fail: reject
    });
  });
}

function chooseImageFromAlbum() {
  return new Promise((resolve, reject) => {
    wx.chooseMedia({
      count: 1,
      mediaType: ["image"],
      sourceType: ["album"],
      success: resolve,
      fail: reject
    });
  });
}

Page({
  data: {
    userName: "Guest",
    hasToken: false,
    loading: false,
    recognized: null,
    backgroundImage: "",
    isMyBird: false
  },

  onShow() {
    const token = wx.getStorageSync("accessToken");
    if (!token) {
      wx.reLaunch({ url: "/pages/login/login" });
      return;
    }

    const userBrief = wx.getStorageSync("userBrief") || {};
    this.setData({
      hasToken: Boolean(token),
      userName: userBrief.username || "Guest"
    });

    this.loadCurrentUser();
  },

  async loadCurrentUser() {
    try {
      const res = await users.getCurrentUser();
      wx.setStorageSync("userBrief", {
        id: res.data.id,
        username: res.data.username,
        avatarUrl: res.data.avatarUrl
      });
      this.setData({ userName: res.data.username || "Guest" });
    } catch (error) {
      if (error && error.statusCode === 401) {
        wx.removeStorageSync("accessToken");
        this.setData({ hasToken: false });
      }
    }
  },

  async handleRecognize(source) {
    if (!requireAuth()) {
      return;
    }

    try {
      const chooseRes = source === "camera" ? await chooseImageFromCamera() : await chooseImageFromAlbum();
      const file = chooseRes.tempFiles && chooseRes.tempFiles[0];
      if (!file || !file.tempFilePath) {
        return;
      }

      this.setData({
        loading: true,
        backgroundImage: file.tempFilePath
      });

      const res = await birds.recognize(file.tempFilePath);
      const matchedBird = findBirdByName(res.data.birdName);
      const recognized = {
        ...res.data,
        confidenceText: toPercent(res.data.confidence),
        fullImageUrl: toFullImageUrl(res.data.imageUrl),
        localTempPath: file.tempFilePath,
        detailId: matchedBird ? matchedBird.id : null
      };

      wx.setStorageSync("latestRecognizeResult", recognized);
      this.setData({
        recognized,
        isMyBird: false
      });
      wx.showToast({ title: "Recognition done", icon: "success" });
    } catch (error) {
      if (error && error.errMsg && error.errMsg.includes("cancel")) {
        if (!this.data.recognized) {
          this.setData({ backgroundImage: "" });
        }
        return;
      }
      wx.showToast({ title: (error && error.message) || "Recognition failed", icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  },

  onStartRecording() {
    this.handleRecognize("camera");
  },

  onSelectPhoto() {
    this.handleRecognize("album");
  },

  onOpenBirdDetail() {
    const { recognized } = this.data;
    if (!recognized || !recognized.birdName) {
      wx.showToast({ title: "No bird recognized yet", icon: "none" });
      return;
    }

    if (recognized.detailId) {
      wx.navigateTo({ url: `/pages/bird-detail/bird-detail?id=${recognized.detailId}` });
      return;
    }

    wx.navigateTo({
      url: `/pages/bird-detail/bird-detail?name=${encodeURIComponent(recognized.birdName)}`
    });
  },

  onMarkAsMyBird() {
    if (!requireAuth()) {
      return;
    }

    const { recognized } = this.data;
    if (!recognized || !recognized.birdName) {
      wx.showToast({ title: "Recognize a bird first", icon: "none" });
      return;
    }

    const list = wx.getStorageSync("myBirds") || [];
    const exists = list.some((item) => item.recordId === recognized.recordId);

    // Persist "recordId -> captured image" mapping so My recordings can always
    // render the actual photo captured by user.
    const recordImageMap = wx.getStorageSync(RECORD_IMAGE_MAP_KEY) || {};
    const recordIdKey = String(recognized.recordId || "");
    const capturedImage = recognized.localTempPath || recognized.fullImageUrl || recognized.imageUrl || "";
    if (recordIdKey && capturedImage) {
      wx.setStorageSync(RECORD_IMAGE_MAP_KEY, {
        ...recordImageMap,
        [recordIdKey]: capturedImage
      });
    }

    if (exists) {
      this.setData({ isMyBird: true });
      wx.showToast({ title: "Already in My Birds", icon: "none" });
      return;
    }

    wx.setStorageSync("myBirds", [
      {
        recordId: recognized.recordId || Date.now(),
        birdName: recognized.birdName,
        imageUrl: recognized.fullImageUrl || recognized.localTempPath || "",
        createdAt: recognized.createdAt || new Date().toISOString(),
        confidence: recognized.confidence
      },
      ...list
    ]);

    this.setData({ isMyBird: true });
    wx.setStorageSync("encyclopediaInitialTab", "records");
    wx.showToast({ title: "Added to My Birds", icon: "success" });
    setTimeout(() => {
      wx.switchTab({ url: "/pages/encyclopedia/encyclopedia" });
    }, 160);
  }
});

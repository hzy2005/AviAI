const { birds, users } = require("../../src/api/index");
const { requireAuth } = require("../../utils/auth");
const { toPercent, toFullImageUrl } = require("../../utils/format");
const { BIRD_KNOWLEDGE, findBirdByName } = require("../../utils/bird-knowledge");

const RECORD_IMAGE_MAP_KEY = "recordImageMap";

function chooseImageFromCamera() {
  return new Promise((resolve, reject) => {
    wx.chooseImage({
      count: 1,
      sourceType: ["camera"],
      sizeType: ["compressed"],
      success: (res) => {
        const firstPath = res.tempFilePaths && res.tempFilePaths[0];
        resolve({
          tempFiles: firstPath ? [{ tempFilePath: firstPath }] : []
        });
      },
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
      this.onQuickSighting();
      return;
    }

    this.addRecordToMyBirds(recognized);
  },

  onQuickSighting() {
    const quickBirds = BIRD_KNOWLEDGE.slice(0, 6).filter((item) => item.commonName || item.chineseName);
    const options = quickBirds.map((item) => item.commonName || item.chineseName);
    if (!quickBirds.length) {
      wx.showToast({ title: "No species data", icon: "none" });
      return;
    }

    wx.showActionSheet({
      itemList: options,
      success: (res) => {
        const selected = quickBirds[res.tapIndex];
        if (!selected) {
          return;
        }

        const manualRecord = {
          recordId: Date.now(),
          birdName: selected.commonName || selected.chineseName || "Unknown Bird",
          imageUrl: "",
          createdAt: new Date().toISOString(),
          confidence: 0,
          confidenceText: "-",
          fullImageUrl: "",
          localTempPath: "",
          detailId: selected.id || null,
          source: "manual"
        };

        wx.setStorageSync("latestRecognizeResult", manualRecord);
        this.setData({
          recognized: manualRecord,
          isMyBird: false
        });

        this.addRecordToMyBirds(manualRecord, "Added as sighting");
      }
    });
  },

  addRecordToMyBirds(record, successTitle = "Added to My Birds") {
    const list = wx.getStorageSync("myBirds") || [];
    const exists = list.some((item) => item.recordId === record.recordId);

    // Persist "recordId -> captured image" mapping so My recordings can always
    // render the actual photo captured by user.
    const recordImageMap = wx.getStorageSync(RECORD_IMAGE_MAP_KEY) || {};
    const recordIdKey = String(record.recordId || "");
    const capturedImage = record.localTempPath || record.fullImageUrl || record.imageUrl || "";
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
        recordId: record.recordId || Date.now(),
        birdName: record.birdName,
        imageUrl: record.fullImageUrl || record.localTempPath || "",
        createdAt: record.createdAt || new Date().toISOString(),
        confidence: record.confidence
      },
      ...list
    ]);

    this.setData({ isMyBird: true });
    wx.setStorageSync("encyclopediaInitialTab", "records");
    wx.showToast({ title: successTitle, icon: "success" });
    setTimeout(() => {
      wx.switchTab({ url: "/pages/encyclopedia/encyclopedia" });
    }, 160);
  }
});

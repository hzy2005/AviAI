const { birds } = require("../../src/api/index");
const { findBirdById, findBirdByName } = require("../../utils/bird-knowledge");
const { formatDateTime, toPercent, toFullImageUrl } = require("../../utils/format");

const ICON_BACK = "/static/icons/return.png";
const ICON_SHARE = "/static/icons/share.png";
const BIRD_IMAGE_FALLBACKS = [
  "/static/view/loginbird.png",
  "/static/view/Cover.jpg",
  "/static/view/index-back.jpg"
];

function normalizeImageList(rawList) {
  if (!Array.isArray(rawList)) {
    return [];
  }

  return rawList
    .map((url) => toFullImageUrl(url))
    .filter((url) => Boolean(url));
}

function getBirdFallbackImages(bird) {
  if (!bird) {
    return [];
  }

  const fromConfig = normalizeImageList(bird.imageUrls);
  if (fromConfig.length) {
    return fromConfig;
  }

  const index = Math.max(0, (Number(bird.id) || 1) - 1) % BIRD_IMAGE_FALLBACKS.length;
  return [BIRD_IMAGE_FALLBACKS[index]];
}

function normalizeRecordFromStorage(raw = {}) {
  const imageList = normalizeImageList(raw.imageUrls);
  const fullImageUrl = toFullImageUrl(raw.fullImageUrl || raw.imageUrl || "");
  const mergedImageList = imageList.length
    ? imageList
    : (fullImageUrl ? [fullImageUrl] : []);

  return {
    recordId: raw.recordId || "",
    birdName: raw.birdName || "-",
    confidenceText: toPercent(raw.confidence),
    createdAtText: formatDateTime(raw.createdAt || Date.now()),
    imageUrl: raw.imageUrl || "",
    imageList: mergedImageList
  };
}

Page({
  data: {
    statusBarHeight: 0,
    mode: "encyclopedia",
    bird: null,
    record: null,
    title: "",
    subtitle: "",
    imageList: [],
    infoRows: [],
    iconBack: ICON_BACK,
    iconShare: ICON_SHARE,
    showShareButton: false
  },

  onLoad(options) {
    const sys = wx.getSystemInfoSync();
    const mode = options.mode === "record" ? "record" : "encyclopedia";

    this.setData({
      statusBarHeight: sys.statusBarHeight || 0,
      mode,
      showShareButton: mode === "record"
    });

    if (mode === "record") {
      this.loadRecordDetail(options);
      return;
    }

    this.loadBirdDetail(options);
  },

  loadBirdDetail(options) {
    const bird =
      findBirdById(options.id) ||
      findBirdByName(options.name ? decodeURIComponent(options.name) : "");

    if (!bird) {
      wx.showToast({ title: "Species not found", icon: "none" });
      setTimeout(() => wx.navigateBack({ delta: 1 }), 300);
      return;
    }

    const infoRows = [
      { label: "Chinese Name", value: bird.chineseName || "-" },
      { label: "English Name", value: bird.commonName || "-" },
      { label: "Scientific Name", value: bird.scientificName || "-" },
      { label: "Conservation", value: bird.confidenceStatus || "-" },
      { label: "Habitat", value: bird.habitat || "-" },
      { label: "Description", value: bird.bio || "-" }
    ];

    this.setData({
      bird,
      record: null,
      title: bird.chineseName || bird.commonName || "Bird Detail",
      subtitle: bird.scientificName || "",
      imageList: getBirdFallbackImages(bird),
      infoRows
    });
  },

  async loadRecordDetail(options) {
    const recordId = String(options.recordId || "");
    const cacheKey = recordId ? `birdDetailRecord-${recordId}` : "";
    const cached = cacheKey ? wx.getStorageSync(cacheKey) : null;
    const latest = wx.getStorageSync("latestRecognizeResult");
    const picked = cached || latest || null;

    let record = picked ? normalizeRecordFromStorage(picked) : null;

    if (!record && recordId) {
      try {
        const res = await birds.getRecords({ page: 1, pageSize: 50 });
        const list = (res.data && res.data.list) || [];
        const matched = list.find((item) => String(item.recordId) === recordId);
        if (matched) {
          record = normalizeRecordFromStorage(matched);
        }
      } catch (error) {
        wx.showToast({ title: error.message || "Load record failed", icon: "none" });
      }
    }

    if (!record) {
      wx.showToast({ title: "Record not found", icon: "none" });
      setTimeout(() => wx.navigateBack({ delta: 1 }), 300);
      return;
    }

    const infoRows = [
      { label: "Record ID", value: record.recordId || "-" },
      { label: "Bird Name", value: record.birdName || "-" },
      { label: "Confidence", value: record.confidenceText || "-" },
      { label: "Created At", value: record.createdAtText || "-" },
      { label: "Image URL", value: record.imageUrl || "-" }
    ];

    this.setData({
      record,
      bird: null,
      title: record.birdName || "My Recording",
      subtitle: "Record Detail",
      imageList: record.imageList,
      infoRows
    });
  },

  onBack() {
    if (getCurrentPages().length > 1) {
      wx.navigateBack({ delta: 1 });
      return;
    }
    wx.switchTab({ url: "/pages/encyclopedia/encyclopedia" });
  },

  onTapShare() {
    wx.showShareMenu({ withShareTicket: true, menus: ["shareAppMessage"] });
  },

  onShareAppMessage() {
    if (this.data.mode !== "record") {
      return {
        title: this.data.title || "Bird Detail",
        path: "/pages/encyclopedia/encyclopedia"
      };
    }

    const imageUrl = (this.data.imageList && this.data.imageList[0]) || "";
    return {
      title: `${this.data.record && this.data.record.birdName ? this.data.record.birdName : "My bird record"}`,
      path: "/pages/encyclopedia/encyclopedia",
      imageUrl
    };
  },

  onPreviewImage(event) {
    const src = event.currentTarget.dataset.src;
    if (!src) {
      return;
    }

    wx.previewImage({
      urls: this.data.imageList,
      current: src
    });
  }
});

const { users } = require("../../src/api/index");
const { requireAuth } = require("../../utils/auth");
const { toFullImageUrl } = require("../../utils/format");
const { isValidEmail } = require("../../utils/validator");

const DEFAULT_AVATAR = "/static/icons/icon-user.png";
const MOCK_USER_STATE_KEY = "mockUserState";
const MOCK_AUTH_STATE_KEY = "mockAuthState";
const MOCK_ALL_STATE_KEY = "mockAllState";
const MOCK_STATE_FILENAME = "avi-ai-mock-state.json";

function saveMockStateFile(state) {
  try {
    if (!wx.env || !wx.env.USER_DATA_PATH || typeof wx.getFileSystemManager !== "function") {
      return;
    }
    const fs = wx.getFileSystemManager();
    const filePath = `${wx.env.USER_DATA_PATH}/${MOCK_STATE_FILENAME}`;
    fs.writeFileSync(filePath, JSON.stringify(state, null, 2), "utf8");
  } catch (error) {}
}

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

Page({
  data: {
    statusBarHeight: 0,
    showPassword: false,
    loading: false,
    form: {
      username: "",
      phone: "",
      email: "",
      password: "",
      confirmPassword: "",
      avatarUrl: DEFAULT_AVATAR
    }
  },

  onLoad() {
    const sys = wx.getSystemInfoSync();
    this.setData({
      statusBarHeight: sys.statusBarHeight || 0
    });
  },

  async onShow() {
    if (!requireAuth()) {
      return;
    }

    const draft = wx.getStorageSync("profileDraft") || {};
    try {
      const res = await users.getCurrentUser();
      this.setData({
        form: {
          username: draft.username || res.data.username || "",
          phone: draft.phone || "",
          email: draft.email || res.data.email || "",
          password: draft.password || "",
          confirmPassword: draft.confirmPassword || "",
          avatarUrl: toFullImageUrl(draft.avatarUrl || res.data.avatarUrl) || DEFAULT_AVATAR
        }
      });
    } catch (error) {
      const cached = wx.getStorageSync("userProfile") || {};
      this.setData({
        form: {
          username: draft.username || cached.username || "",
          phone: draft.phone || "",
          email: draft.email || cached.email || "",
          password: draft.password || "",
          confirmPassword: draft.confirmPassword || "",
          avatarUrl: toFullImageUrl(draft.avatarUrl || cached.avatarUrl) || DEFAULT_AVATAR
        }
      });
      if (!draft.email && !cached.email) {
        wx.showToast({ title: error.message || "Load failed", icon: "none" });
      }
    }
  },

  onBack() {
    wx.navigateBack({ delta: 1 });
  },

  onInput(event) {
    const key = event.currentTarget.dataset.key;
    const value = event.detail.value;
    this.setData({
      [`form.${key}`]: key === "password" || key === "confirmPassword" ? value : value.trim()
    });
  },

  togglePassword() {
    this.setData({
      showPassword: !this.data.showPassword
    });
  },

  async onChooseAvatar() {
    if (!requireAuth()) {
      return;
    }

    try {
      const chooseRes = await chooseSingleImage();
      const file = chooseRes.tempFiles && chooseRes.tempFiles[0];
      if (!file || !file.tempFilePath) {
        return;
      }
      this.setData({
        "form.avatarUrl": file.tempFilePath
      });
    } catch (error) {
      if (error && error.errMsg && error.errMsg.includes("cancel")) {
        return;
      }
      wx.showToast({ title: "Avatar update failed", icon: "none" });
    }
  },

  onDone() {
    const { form } = this.data;

    if (!form.username || !form.email || !form.password || !form.confirmPassword) {
      wx.showToast({ title: "Please complete required fields", icon: "none" });
      return;
    }

    if (!isValidEmail(form.email)) {
      wx.showToast({ title: "Please enter a valid email", icon: "none" });
      return;
    }

    if (form.password && form.password.length < 8) {
      wx.showToast({ title: "Password must be at least 8 characters", icon: "none" });
      return;
    }

    if (form.password !== form.confirmPassword) {
      wx.showToast({ title: "Passwords do not match", icon: "none" });
      return;
    }

    wx.setStorageSync("profileDraft", form);

    // Keep local profile display in sync. API docs currently provide no user update endpoint.
    const userProfile = wx.getStorageSync("userProfile") || {};
    const nextUserProfile = {
      ...userProfile,
      email: form.email,
      username: form.username,
      avatarUrl: form.avatarUrl || userProfile.avatarUrl || ""
    };
    wx.setStorageSync("userProfile", nextUserProfile);

    // Keep mock auth/profile state in sync for temporary mock-only backend mode.
    wx.setStorageSync(MOCK_USER_STATE_KEY, {
      ...nextUserProfile
    });
    wx.setStorageSync(MOCK_AUTH_STATE_KEY, {
      email: form.email,
      password: form.password
    });
    const existingAll = wx.getStorageSync(MOCK_ALL_STATE_KEY) || {};
    const nextAllState = {
      ...existingAll,
      user: {
        ...(existingAll.user || {}),
        ...nextUserProfile
      },
      auth: {
        ...(existingAll.auth || {}),
        email: form.email,
        password: form.password
      }
    };
    wx.setStorageSync(MOCK_ALL_STATE_KEY, nextAllState);
    saveMockStateFile(nextAllState);

    wx.showToast({
      title: "Saved locally",
      icon: "success"
    });

    setTimeout(() => {
      wx.navigateBack({ delta: 1 });
    }, 220);
  },

  onCancel() {
    wx.navigateBack({ delta: 1 });
  }
});

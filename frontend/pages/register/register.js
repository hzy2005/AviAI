const { isValidEmail } = require("../../utils/validator");

Page({
  data: {
    fullName: "",
    mobile: "",
    email: "",
    password: "",
    confirmPassword: "",
    loading: false,
    showPassword: false
  },

  onInput(event) {
    const { key } = event.currentTarget.dataset;
    const value = event.detail.value;
    this.setData({ [key]: key === "password" || key === "confirmPassword" ? value : value.trim() });
  },

  onGoSignIn() {
    wx.redirectTo({ url: "/pages/login/login" });
  },

  togglePassword() {
    this.setData({
      showPassword: !this.data.showPassword
    });
  },

  async onSignUp() {
    const { fullName, mobile, email, password, confirmPassword } = this.data;
    const { auth } = require("../../src/api/index");

    if (!fullName || !email || !password || !confirmPassword) {
      wx.showToast({ title: "Please complete all fields", icon: "none" });
      return;
    }

    if (!isValidEmail(email)) {
      wx.showToast({ title: "Please enter a valid email", icon: "none" });
      return;
    }

    if (password.length < 8) {
      wx.showToast({ title: "Password must be at least 8 characters", icon: "none" });
      return;
    }

    if (password !== confirmPassword) {
      wx.showToast({ title: "Passwords do not match", icon: "none" });
      return;
    }

    this.setData({ loading: true });

    try {
      await auth.register({
        username: fullName,
        email,
        password
      });

      // Keep local draft aligned with registration inputs.
      wx.setStorageSync("profileDraft", {
        username: fullName,
        phone: mobile || "",
        email,
        password,
        confirmPassword,
        avatarUrl: ""
      });

      wx.showToast({ title: "Registered successfully", icon: "success" });
      setTimeout(() => {
        wx.redirectTo({ url: "/pages/login/login" });
      }, 260);
    } catch (error) {
      wx.showToast({
        title: error.message || "Register failed",
        icon: "none"
      });
    } finally {
      this.setData({ loading: false });
    }
  }
});

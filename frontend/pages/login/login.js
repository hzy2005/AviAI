const { isValidEmail } = require("../../utils/validator");

Page({
  data: {
    email: "",
    password: "",
    loading: false,
    showPassword: false
  },

  onEmailInput(event) {
    this.setData({ email: event.detail.value.trim() });
  },

  onPasswordInput(event) {
    this.setData({ password: event.detail.value });
  },

  onGoSignup() {
    wx.navigateTo({ url: "/pages/register/register" });
  },

  togglePassword() {
    this.setData({
      showPassword: !this.data.showPassword
    })
  },


  async onSignIn() {
    const { email, password } = this.data;
    const { auth } = require("../../src/api/index");

    if (!email || !password) {
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

    this.setData({ loading: true });

    try {
      await auth.login({ email, password });
      wx.showToast({ title: "Login successful", icon: "success" });
      setTimeout(() => {
        wx.switchTab({ url: "/pages/index/index" });
      }, 220);
    } catch (error) {
      wx.showToast({
        title: error.message || "Login failed",
        icon: "none"
      });
    } finally {
      this.setData({ loading: false });
    }
  }
});

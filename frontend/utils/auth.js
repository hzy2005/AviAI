function hasToken() {
  return Boolean(wx.getStorageSync("accessToken"));
}

function requireAuth(options = {}) {
  const { tip = "请先登录", redirect = true } = options;
  if (hasToken()) {
    return true;
  }

  wx.showToast({
    title: tip,
    icon: "none"
  });

  if (redirect) {
    setTimeout(() => {
      wx.navigateTo({ url: "/pages/login/login" });
    }, 200);
  }

  return false;
}

module.exports = {
  hasToken,
  requireAuth
};

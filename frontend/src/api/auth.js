const { apiClient } = require("./client");

function register(data) {
  return apiClient({
    url: "/api/v1/auth/register",
    method: "POST",
    data
  });
}

function login(data) {
  return apiClient({
    url: "/api/v1/auth/login",
    method: "POST",
    data
  }).then(async (res) => {
    if (res.data && res.data.token) {
      wx.setStorageSync("accessToken", res.data.token);
      wx.setStorageSync("userBrief", res.data.user || null);

      // Align profile display with API docs: fetch authoritative user info
      // from GET /api/v1/users/me after login.
      try {
        const me = await apiClient({
          url: "/api/v1/users/me"
        });
        if (me && me.data) {
          wx.setStorageSync("userProfile", me.data);
        }
      } catch {
        // Keep login successful even if profile sync fails.
      }
    }
    return res;
  }).catch((error) => {
    // Ensure failed login cannot keep stale authenticated state.
    wx.removeStorageSync("accessToken");
    wx.removeStorageSync("userBrief");
    wx.removeStorageSync("userProfile");
    throw error;
  });
}

function logout() {
  return apiClient({
    url: "/api/v1/auth/logout",
    method: "POST"
  }).then((res) => {
    wx.removeStorageSync("accessToken");
    wx.removeStorageSync("userBrief");
    wx.removeStorageSync("userProfile");
    return res;
  });
}

module.exports = {
  register,
  login,
  logout
};

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
  }).then((res) => {
    if (res.data && res.data.token) {
      wx.setStorageSync("accessToken", res.data.token);
    }
    return res;
  });
}

function logout() {
  return apiClient({
    url: "/api/v1/auth/logout",
    method: "POST"
  }).then((res) => {
    wx.removeStorageSync("accessToken");
    return res;
  });
}

module.exports = {
  register,
  login,
  logout
};

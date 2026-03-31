const { apiClient } = require("./client");
const { baseUrl } = require("../../config/env");

function recognize(filePath) {
  const token = wx.getStorageSync("accessToken");

  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: `${baseUrl}/api/v1/birds/recognize`,
      filePath,
      name: "image",
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (res) => {
        const data = JSON.parse(res.data || "{}");
        if (res.statusCode >= 200 && res.statusCode < 300 && data.code === 0) {
          resolve(data);
          return;
        }
        reject(data);
      },
      fail: reject
    });
  });
}

function getRecords(params = {}) {
  const { page = 1, pageSize = 10 } = params;
  return apiClient({
    url: `/api/v1/birds/records?page=${page}&pageSize=${pageSize}`
  });
}

module.exports = {
  recognize,
  getRecords
};

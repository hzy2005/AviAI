const { apiClient } = require("./client");
const { baseUrl, enableOfflineMock, preferOfflineMock } = require("../../config/env");
const { getMockRecognizeResponse } = require("../../utils/mock-api");

function recognize(filePath) {
  const token = wx.getStorageSync("accessToken");

  return new Promise((resolve, reject) => {
    if (preferOfflineMock && enableOfflineMock) {
      resolve(getMockRecognizeResponse(filePath));
      return;
    }

    wx.uploadFile({
      url: `${baseUrl}/api/v1/birds/recognize`,
      filePath,
      name: "image",
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (res) => {
        let data = {};
        try {
          data = JSON.parse(res.data || "{}");
        } catch {
          data = {};
        }
        if (res.statusCode >= 200 && res.statusCode < 300 && data.code === 0) {
          resolve(data);
          return;
        }
        reject(data);
      },
      fail: (error) => {
        if (enableOfflineMock && error && error.errMsg && error.errMsg.indexOf("request:fail") >= 0) {
          resolve(getMockRecognizeResponse(filePath));
          return;
        }
        reject(error);
      }
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

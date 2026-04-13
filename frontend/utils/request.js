const { baseUrl, enableOfflineMock, preferOfflineMock } = require("../config/env");
const { getMockResponse } = require("./mock-api");

const OFFLINE_COOLDOWN_MS = 15000;
let offlineUntil = 0;

function isNetworkFail(error) {
  return Boolean(error && error.errMsg && error.errMsg.indexOf("request:fail") >= 0);
}

function buildNetworkError(rawError) {
  return {
    code: -1,
    message: "无法连接后端，请先启动 FastAPI 服务（uvicorn）。",
    data: null,
    isNetworkError: true,
    errMsg: rawError && rawError.errMsg ? rawError.errMsg : "network unavailable"
  };
}

function handleMockResult(mockData, reject, resolve) {
  if (!mockData) {
    return false;
  }

  if (Number(mockData.code) === 0) {
    resolve(mockData);
    return true;
  }

  reject({
    statusCode: 400,
    ...mockData
  });
  return true;
}

function request({ url, method = "GET", data, header = {} }) {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync("accessToken");
    const currentMethod = (method || "GET").toUpperCase();

    if (preferOfflineMock && enableOfflineMock) {
      const mockData = getMockResponse({ url, method: currentMethod, data, token });
      if (handleMockResult(mockData, reject, resolve)) {
        return;
      }
    }

    if (Date.now() < offlineUntil) {
      if (enableOfflineMock) {
        const mockData = getMockResponse({ url, method: currentMethod, data, token });
        if (handleMockResult(mockData, reject, resolve)) {
          return;
        }
      }
      reject(buildNetworkError());
      return;
    }

    wx.request({
      url: `${baseUrl}${url}`,
      method: currentMethod,
      data,
      timeout: 10000,
      header: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...header
      },
      success: (res) => {
        const responseData = res.data || {};

        if (res.statusCode >= 200 && res.statusCode < 300 && responseData.code === 0) {
          resolve(responseData);
          return;
        }

        reject({
          statusCode: res.statusCode,
          ...responseData
        });
      },
      fail: (err) => {
        if (isNetworkFail(err)) {
          offlineUntil = Date.now() + OFFLINE_COOLDOWN_MS;
          if (enableOfflineMock) {
            const mockData = getMockResponse({ url, method: currentMethod, data, token });
            if (handleMockResult(mockData, reject, resolve)) {
              return;
            }
          }
          reject(buildNetworkError(err));
          return;
        }

        reject(err);
      }
    });
  });
}

module.exports = {
  request,
  isNetworkError: (error) => Boolean(error && error.isNetworkError)
};

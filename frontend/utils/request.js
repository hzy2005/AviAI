const { baseUrl } = require("../config/env");

function request({ url, method = "GET", data, header = {} }) {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync("accessToken");

    wx.request({
      url: `${baseUrl}${url}`,
      method,
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
      fail: (err) => reject(err)
    });
  });
}

module.exports = {
  request
};

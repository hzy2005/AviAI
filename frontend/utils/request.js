const { baseUrl } = require("../config/env");

function request({ url, method = "GET", data, header = {} }) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${baseUrl}${url}`,
      method,
      data,
      timeout: 10000,
      header: {
        "Content-Type": "application/json",
        ...header
      },
      success: (res) => resolve(res.data),
      fail: (err) => reject(err)
    });
  });
}

module.exports = {
  request
};

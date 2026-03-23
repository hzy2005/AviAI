const { request } = require("../../utils/request");

Page({
  data: {
    loading: false,
    resultText: "点击按钮后显示 /api/v1/health 返回结果..."
  },

  async onCheckHealth() {
    this.setData({
      loading: true,
      resultText: "请求中..."
    });

    try {
      const data = await request({
        url: "/api/v1/health",
        method: "GET"
      });

      this.setData({
        resultText: JSON.stringify(data, null, 2)
      });
    } catch (error) {
      this.setData({
        resultText: `请求失败: ${error.errMsg || "unknown error"}`
      });
    } finally {
      this.setData({
        loading: false
      });
    }
  }
});

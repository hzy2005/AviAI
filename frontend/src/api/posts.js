const { apiClient } = require("./client");
const { baseUrl } = require("../../config/env");

function create(data) {
  return apiClient({
    url: "/api/v1/posts",
    method: "POST",
    data
  });
}

function aiCopywriting(data) {
  return apiClient({
    url: "/api/v1/posts/ai-copywriting",
    method: "POST",
    data
  });
}

function uploadImage(filePath) {
  const token = wx.getStorageSync("accessToken");

  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: `${baseUrl}/api/v1/posts/upload-image`,
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
      fail: reject
    });
  });
}

function list(params = {}) {
  const { page = 1, pageSize = 10, keyword = "" } = params;
  const query = `page=${page}&pageSize=${pageSize}&keyword=${encodeURIComponent(keyword)}`;
  return apiClient({
    url: `/api/v1/posts?${query}`
  });
}

function detail(postId) {
  return apiClient({
    url: `/api/v1/posts/${postId}`
  });
}

function update(postId, data) {
  return apiClient({
    url: `/api/v1/posts/${postId}`,
    method: "PUT",
    data
  });
}

function remove(postId) {
  return apiClient({
    url: `/api/v1/posts/${postId}`,
    method: "DELETE"
  });
}

function like(postId) {
  return apiClient({
    url: `/api/v1/posts/${postId}/like`,
    method: "POST"
  });
}

function comment(postId, data) {
  return apiClient({
    url: `/api/v1/posts/${postId}/comments`,
    method: "POST",
    data
  });
}

module.exports = {
  create,
  aiCopywriting,
  uploadImage,
  list,
  detail,
  update,
  remove,
  like,
  comment
};

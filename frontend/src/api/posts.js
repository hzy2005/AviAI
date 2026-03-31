const { apiClient } = require("./client");

function create(data) {
  return apiClient({
    url: "/api/v1/posts",
    method: "POST",
    data
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
  list,
  detail,
  update,
  remove,
  like,
  comment
};

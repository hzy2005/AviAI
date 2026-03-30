const mockPosts = [
  {
    postId: 1001,
    content: "今天在湿地拍到了白鹭！",
    imageUrl: "/uploads/post_001.jpg",
    likeCount: 12,
    commentCount: 3,
    createdAt: "2026-03-30T08:00:00Z",
    author: {
      id: 1,
      username: "birdlover",
      avatarUrl: ""
    }
  }
];

function getMockPostsResponse() {
  return {
    code: 0,
    message: "ok",
    data: {
      list: mockPosts,
      total: mockPosts.length,
      page: 1,
      pageSize: 10
    }
  };
}

module.exports = {
  mockPosts,
  getMockPostsResponse
};

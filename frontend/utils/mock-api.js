const MOCK_DEFAULT_USER = {
  id: 1,
  username: "birdlover",
  email: "bird@example.com",
  avatarUrl: "",
  createdAt: "2026-03-09T10:30:00Z"
};

const MOCK_DEFAULT_AUTH_STATE = {
  email: "bird@example.com",
  password: "12345678"
};

const MOCK_USER_STATE_KEY = "mockUserState";
const MOCK_AUTH_STATE_KEY = "mockAuthState";
const MOCK_ALL_STATE_KEY = "mockAllState";
const MOCK_STATE_FILENAME = "avi-ai-mock-state.json";

const DEFAULT_POSTS = [
  {
    postId: 1001,
    content: "好漂亮的小鸟",
    imageUrl: "/static/view/loginbird.png",
    imageUrls: ["/static/view/loginbird.png"],
    likeCount: 12,
    commentCount: 3,
    createdAt: "2026-03-09T12:00:00Z",
    updatedAt: "2026-03-09T12:00:00Z",
    author: {
      id: 1,
      username: "birdlover",
      avatarUrl: ""
    }
  },
  {
    postId: 1002,
    content: "This week I spotted a common kingfisher, the colors were amazing.",
    imageUrl: "/static/view/Cover.jpg",
    imageUrls: ["/static/view/Cover.jpg"],
    likeCount: 7,
    commentCount: 1,
    createdAt: "2026-03-08T09:22:00Z",
    updatedAt: "2026-03-08T09:22:00Z",
    author: {
      id: 2,
      username: "wildcam",
      avatarUrl: ""
    }
  }
];

const DEFAULT_RECORDS = [
  {
    recordId: 301,
    birdName: "戴胜",
    confidence: 0.94,
    imageUrl: "",
    createdAt: "2026-03-09T10:35:00Z"
  },
  {
    recordId: 302,
    birdName: "Common Kingfisher",
    confidence: 0.89,
    imageUrl: "",
    createdAt: "2026-03-08T08:15:00Z"
  },
  {
    recordId: 303,
    birdName: "Mallard",
    confidence: 0.91,
    imageUrl: "",
    createdAt: "2026-03-07T07:02:00Z"
  }
];

let mockUser = {
  ...MOCK_DEFAULT_USER
};

let mockAuthState = {
  ...MOCK_DEFAULT_AUTH_STATE
};

let mockPosts = [...DEFAULT_POSTS];
let mockRecords = [...DEFAULT_RECORDS];

function ok(data) {
  return {
    code: 0,
    message: "ok",
    data
  };
}

function fail(code, message) {
  return {
    code,
    message,
    data: null
  };
}

function getStorageSyncSafe(key) {
  try {
    if (typeof wx !== "undefined" && typeof wx.getStorageSync === "function") {
      return wx.getStorageSync(key);
    }
  } catch (error) {}
  return null;
}

function setStorageSyncSafe(key, value) {
  try {
    if (typeof wx !== "undefined" && typeof wx.setStorageSync === "function") {
      wx.setStorageSync(key, value);
    }
  } catch (error) {}
}

function getFileSystemManagerSafe() {
  try {
    if (typeof wx !== "undefined" && typeof wx.getFileSystemManager === "function") {
      return wx.getFileSystemManager();
    }
  } catch (error) {}
  return null;
}

function getStateFilePath() {
  try {
    if (typeof wx !== "undefined" && wx.env && wx.env.USER_DATA_PATH) {
      return `${wx.env.USER_DATA_PATH}/${MOCK_STATE_FILENAME}`;
    }
  } catch (error) {}
  return "";
}

function readStateFromFile() {
  const fs = getFileSystemManagerSafe();
  const filePath = getStateFilePath();
  if (!fs || !filePath) {
    return null;
  }

  try {
    const raw = fs.readFileSync(filePath, "utf8");
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch (error) {
    return null;
  }
}

function writeStateToFile(state) {
  const fs = getFileSystemManagerSafe();
  const filePath = getStateFilePath();
  if (!fs || !filePath) {
    return;
  }

  try {
    fs.writeFileSync(filePath, JSON.stringify(state, null, 2), "utf8");
  } catch (error) {}
}

function getCurrentStateSnapshot() {
  return {
    user: mockUser,
    auth: mockAuthState,
    posts: mockPosts,
    records: mockRecords
  };
}

function applyState(persisted = {}) {
  if (persisted.user && typeof persisted.user === "object") {
    mockUser = {
      ...mockUser,
      ...persisted.user
    };
  }

  if (persisted.auth && typeof persisted.auth === "object") {
    mockAuthState = {
      ...mockAuthState,
      ...persisted.auth
    };
  }

  if (Array.isArray(persisted.posts)) {
    mockPosts = [...persisted.posts];
  }

  if (Array.isArray(persisted.records)) {
    mockRecords = [...persisted.records];
  }
}

function loadPersistedState() {
  const allFromFile = readStateFromFile();
  if (allFromFile) {
    applyState(allFromFile);
  }

  const allFromStorage = getStorageSyncSafe(MOCK_ALL_STATE_KEY);
  if (allFromStorage && typeof allFromStorage === "object") {
    applyState(allFromStorage);
  }

  const persistedUser = getStorageSyncSafe(MOCK_USER_STATE_KEY);
  if (persistedUser && typeof persistedUser === "object") {
    mockUser = {
      ...mockUser,
      ...persistedUser
    };
  }

  const persistedAuth = getStorageSyncSafe(MOCK_AUTH_STATE_KEY);
  if (persistedAuth && typeof persistedAuth === "object") {
    mockAuthState = {
      ...mockAuthState,
      ...persistedAuth
    };
  }
}

function persistAllState() {
  const snapshot = getCurrentStateSnapshot();
  setStorageSyncSafe(MOCK_ALL_STATE_KEY, snapshot);
  setStorageSyncSafe(MOCK_USER_STATE_KEY, snapshot.user);
  setStorageSyncSafe(MOCK_AUTH_STATE_KEY, snapshot.auth);
  writeStateToFile(snapshot);
}

function hasToken(token) {
  return Boolean(String(token || "").trim());
}

function requireTokenOrFail(token) {
  if (hasToken(token)) {
    return null;
  }
  return fail(1002, "未登录或 Token 无效");
}

function isValidEmail(email) {
  const value = String(email || "").trim();
  return /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(value);
}

function parseQuery(url) {
  const index = url.indexOf("?");
  if (index < 0) {
    return {};
  }
  const query = url.slice(index + 1);
  return query.split("&").reduce((acc, pair) => {
    const [rawKey, rawValue = ""] = pair.split("=");
    if (!rawKey) {
      return acc;
    }
    acc[decodeURIComponent(rawKey)] = decodeURIComponent(rawValue);
    return acc;
  }, {});
}

function paginate(list, page, pageSize) {
  const safePage = Math.max(1, Number(page) || 1);
  const safePageSize = Math.max(1, Number(pageSize) || 10);
  const start = (safePage - 1) * safePageSize;
  const end = start + safePageSize;
  return list.slice(start, end);
}

function getMockResponse({ url, method = "GET", data, token }) {
  loadPersistedState();

  const normalizedMethod = method.toUpperCase();
  const path = url.split("?")[0];
  const query = parseQuery(url);

  if (path === "/api/v1/health" && normalizedMethod === "GET") {
    return ok({
      service: "backend",
      status: "mock",
      database: "mock",
      time: new Date().toISOString()
    });
  }

  if (path === "/api/v1/auth/register" && normalizedMethod === "POST") {
    const username = String((data && data.username) || "").trim();
    const email = String((data && data.email) || "").trim();
    const password = String((data && data.password) || "");

    if (!username || !email || !password || !isValidEmail(email) || password.length < 8) {
      return fail(1001, "参数错误");
    }

    mockUser = {
      ...mockUser,
      username,
      email,
      createdAt: new Date().toISOString()
    };

    mockAuthState = {
      ...mockAuthState,
      email,
      password
    };

    persistAllState();
    return ok({ userId: mockUser.id });
  }

  if (path === "/api/v1/auth/login" && normalizedMethod === "POST") {
    const email = String((data && data.email) || "").trim();
    const password = String((data && data.password) || "");

    if (!email || !password || !isValidEmail(email) || password.length < 8) {
      return fail(1001, "参数错误");
    }

    if (email !== mockAuthState.email || password !== mockAuthState.password) {
      return fail(1002, "未登录或 Token 无效");
    }

    return ok({
      token: "mock-jwt-token",
      user: {
        id: mockUser.id,
        username: mockUser.username,
        avatarUrl: mockUser.avatarUrl || ""
      }
    });
  }

  if (path === "/api/v1/auth/logout" && normalizedMethod === "POST") {
    return ok({ success: true });
  }

  if (path === "/api/v1/users/me" && normalizedMethod === "GET") {
    const authError = requireTokenOrFail(token);
    if (authError) {
      return authError;
    }
    return ok(mockUser);
  }

  if (path === "/api/v1/birds/records" && normalizedMethod === "GET") {
    const authError = requireTokenOrFail(token);
    if (authError) {
      return authError;
    }

    const page = Number(query.page || 1);
    const pageSize = Number(query.pageSize || 10);
    return ok({
      list: paginate(mockRecords, page, pageSize),
      total: mockRecords.length,
      page,
      pageSize
    });
  }

  if (path === "/api/v1/posts" && normalizedMethod === "GET") {
    const page = Number(query.page || 1);
    const pageSize = Number(query.pageSize || 10);
    const keyword = (query.keyword || "").trim();
    const filtered = keyword
      ? mockPosts.filter((item) => item.content.indexOf(keyword) >= 0)
      : mockPosts;

    return ok({
      list: paginate(filtered, page, pageSize),
      total: filtered.length,
      page,
      pageSize
    });
  }

  if (path === "/api/v1/posts" && normalizedMethod === "POST") {
    const authError = requireTokenOrFail(token);
    if (authError) {
      return authError;
    }

    const postId = Date.now();
    const imageUrl = (data && data.imageUrl) || "";
    const now = new Date().toISOString();
    const newPost = {
      postId,
      content: (data && data.content) || "",
      imageUrl,
      imageUrls: imageUrl ? [imageUrl] : [],
      likeCount: 0,
      commentCount: 0,
      createdAt: now,
      updatedAt: now,
      author: {
        id: mockUser.id,
        username: mockUser.username,
        avatarUrl: mockUser.avatarUrl || ""
      }
    };
    mockPosts = [newPost, ...mockPosts];
    persistAllState();
    return ok({ postId });
  }

  const detailMatch = path.match(/^\/api\/v1\/posts\/(\d+)$/);
  if (detailMatch && normalizedMethod === "GET") {
    const postId = Number(detailMatch[1]);
    const detail = mockPosts.find((item) => item.postId === postId);
    if (!detail) {
      return fail(1004, "资源不存在");
    }
    return ok(detail);
  }

  if (detailMatch && normalizedMethod === "PUT") {
    const authError = requireTokenOrFail(token);
    if (authError) {
      return authError;
    }

    const postId = Number(detailMatch[1]);
    const target = mockPosts.find((item) => item.postId === postId);
    if (!target) {
      return fail(1004, "资源不存在");
    }

    const nextContent = String((data && data.content) || target.content || "").trim();
    const nextImageUrl = data && Object.prototype.hasOwnProperty.call(data, "imageUrl")
      ? (data.imageUrl || "")
      : target.imageUrl;

    mockPosts = mockPosts.map((item) => {
      if (item.postId !== postId) {
        return item;
      }
      return {
        ...item,
        content: nextContent || item.content,
        imageUrl: nextImageUrl,
        imageUrls: nextImageUrl ? [nextImageUrl] : [],
        updatedAt: new Date().toISOString()
      };
    });

    persistAllState();
    return ok({ postId });
  }

  if (detailMatch && normalizedMethod === "DELETE") {
    const authError = requireTokenOrFail(token);
    if (authError) {
      return authError;
    }

    const postId = Number(detailMatch[1]);
    const before = mockPosts.length;
    mockPosts = mockPosts.filter((item) => item.postId !== postId);
    if (mockPosts.length === before) {
      return fail(1004, "资源不存在");
    }
    persistAllState();
    return ok({ postId, deleted: true });
  }

  const likeMatch = path.match(/^\/api\/v1\/posts\/(\d+)\/like$/);
  if (likeMatch && normalizedMethod === "POST") {
    const authError = requireTokenOrFail(token);
    if (authError) {
      return authError;
    }

    const postId = Number(likeMatch[1]);
    const target = mockPosts.find((item) => item.postId === postId);
    if (!target) {
      return fail(1004, "资源不存在");
    }

    mockPosts = mockPosts.map((post) => {
      if (post.postId !== postId) {
        return post;
      }
      return {
        ...post,
        likeCount: post.likeCount + 1
      };
    });
    persistAllState();
    return ok({ postId, liked: true });
  }

  const commentMatch = path.match(/^\/api\/v1\/posts\/(\d+)\/comments$/);
  if (commentMatch && normalizedMethod === "POST") {
    const authError = requireTokenOrFail(token);
    if (authError) {
      return authError;
    }

    const postId = Number(commentMatch[1]);
    const target = mockPosts.find((item) => item.postId === postId);
    if (!target) {
      return fail(1004, "资源不存在");
    }

    mockPosts = mockPosts.map((post) => {
      if (post.postId !== postId) {
        return post;
      }
      return {
        ...post,
        commentCount: post.commentCount + 1
      };
    });
    persistAllState();
    return ok({ commentId: Date.now() });
  }

  return null;
}

function getMockRecognizeResponse(filePath = "") {
  loadPersistedState();

  const createdAt = new Date().toISOString();
  const record = {
    recordId: Date.now(),
    birdName: "Eurasian Hoopoe",
    confidence: 0.92,
    imageUrl: filePath || "/static/view/loginbird.png",
    createdAt
  };

  // Keep mock behavior aligned with API docs:
  // POST /birds/recognize should create a new record visible in GET /birds/records.
  mockRecords = [record, ...mockRecords];
  persistAllState();

  return ok(record);
}

module.exports = {
  getMockResponse,
  getMockRecognizeResponse
};

const test = require("node:test");
const assert = require("node:assert/strict");

const {
  createSpy,
  createWxMock,
  mockModule,
  clearModule
} = require("./helpers/test-utils");

test("auth.login stores token, brief profile and full profile after success", async () => {
  const { storage } = createWxMock();
  const apiClientSpy = createSpy((config) => {
    if (config.url === "/api/v1/auth/login") {
      return Promise.resolve({
        code: 0,
        data: {
          token: "mock-token",
          user: { id: 1, username: "birdlover", avatarUrl: "" }
        }
      });
    }

    if (config.url === "/api/v1/users/me") {
      return Promise.resolve({
        code: 0,
        data: {
          id: 1,
          username: "birdlover",
          email: "bird@example.com"
        }
      });
    }

    return Promise.reject(new Error("unexpected request"));
  });
  const restoreClient = mockModule("src/api/client.js", {
    apiClient: apiClientSpy
  });

  clearModule("src/api/auth.js");
  const auth = require("../api/auth");

  const result = await auth.login({
    email: "bird@example.com",
    password: "12345678"
  });

  assert.equal(result.data.token, "mock-token");
  assert.equal(storage.get("accessToken"), "mock-token");
  assert.deepEqual(storage.get("userBrief"), {
    id: 1,
    username: "birdlover",
    avatarUrl: ""
  });
  assert.deepEqual(storage.get("userProfile"), {
    id: 1,
    username: "birdlover",
    email: "bird@example.com"
  });

  restoreClient();
});

test("auth.login clears stale auth state after failed login", async () => {
  const { storage } = createWxMock({
    initialStorage: {
      accessToken: "stale-token",
      userBrief: { id: 99 },
      userProfile: { id: 99 }
    }
  });
  const restoreClient = mockModule("src/api/client.js", {
    apiClient: createSpy(() => Promise.reject({ message: "Login failed" }))
  });

  clearModule("src/api/auth.js");
  const auth = require("../api/auth");

  await assert.rejects(
    auth.login({ email: "bird@example.com", password: "wrongpass" }),
    { message: "Login failed" }
  );
  assert.equal(storage.has("accessToken"), false);
  assert.equal(storage.has("userBrief"), false);
  assert.equal(storage.has("userProfile"), false);

  restoreClient();
});

test("birds.recognize falls back to mock response on network failure", async () => {
  createWxMock({
    uploadFile: createSpy(({ fail }) => {
      fail({ errMsg: "uploadFile:fail request:fail" });
    })
  });
  const restoreEnv = mockModule("config/env.js", {
    baseUrl: "http://127.0.0.1:8000",
    enableOfflineMock: true,
    preferOfflineMock: false
  });
  const restoreMockApi = mockModule("utils/mock-api.js", {
    getMockRecognizeResponse: createSpy((filePath) => ({
      code: 0,
      data: {
        recordId: 1,
        birdName: "Eurasian Hoopoe",
        confidence: 0.92,
        imageUrl: filePath
      }
    }))
  });

  clearModule("src/api/birds.js");
  const birds = require("../api/birds");
  const result = await birds.recognize("wxfile://bird.jpg");

  assert.equal(result.code, 0);
  assert.equal(result.data.imageUrl, "wxfile://bird.jpg");

  restoreMockApi();
  restoreEnv();
});

test("birds.getRecords builds request url from api contract", async () => {
  createWxMock();
  const apiClientSpy = createSpy((config) => Promise.resolve(config));
  const restoreClient = mockModule("src/api/client.js", {
    apiClient: apiClientSpy
  });

  clearModule("src/api/birds.js");
  const birds = require("../api/birds");
  await birds.getRecords({ page: 2, pageSize: 5 });

  assert.equal(apiClientSpy.calls.length, 1);
  assert.equal(apiClientSpy.calls[0][0].url, "/api/v1/birds/records?page=2&pageSize=5");

  restoreClient();
});

test("posts.uploadImage sends token and resolves parsed response", async () => {
  const { wx } = createWxMock({
    initialStorage: {
      accessToken: "mock-token"
    },
    uploadFile: createSpy(({ header, success, url, filePath, name }) => {
      assert.equal(url, "http://127.0.0.1:8000/api/v1/posts/upload-image");
      assert.equal(filePath, "wxfile://cover.jpg");
      assert.equal(name, "image");
      assert.deepEqual(header, {
        Authorization: "Bearer mock-token"
      });
      success({
        statusCode: 200,
        data: JSON.stringify({
          code: 0,
          message: "ok",
          data: {
            imageUrl: "/uploads/cover.jpg"
          }
        })
      });
    })
  });
  const restoreEnv = mockModule("config/env.js", {
    baseUrl: "http://127.0.0.1:8000"
  });

  clearModule("src/api/posts.js");
  const posts = require("../api/posts");
  const result = await posts.uploadImage("wxfile://cover.jpg");

  assert.equal(wx.uploadFile.calls.length, 1);
  assert.equal(result.data.imageUrl, "/uploads/cover.jpg");

  restoreEnv();
});

test("mock api requires token for users.me and follows code/message/data shape", () => {
  createWxMock();
  clearModule("utils/mock-api.js");
  const { getMockResponse } = require("../../utils/mock-api");

  const response = getMockResponse({
    url: "/api/v1/users/me",
    method: "GET",
    token: ""
  });

  assert.deepEqual(response, {
    code: 1002,
    message: "未登录或 Token 无效",
    data: null
  });
});

test("mock api filters post list by keyword with paginated data", () => {
  createWxMock();
  clearModule("utils/mock-api.js");
  const { getMockResponse } = require("../../utils/mock-api");

  const response = getMockResponse({
    url: "/api/v1/posts?page=1&pageSize=10&keyword=kingfisher",
    method: "GET"
  });

  assert.equal(response.code, 0);
  assert.equal(response.data.total, 1);
  assert.equal(response.data.list.length, 1);
  assert.match(response.data.list[0].content, /kingfisher/i);
});

test.afterEach(() => {
  delete global.wx;
  clearModule("src/api/auth.js");
  clearModule("src/api/birds.js");
  clearModule("src/api/posts.js");
  clearModule("utils/mock-api.js");
});

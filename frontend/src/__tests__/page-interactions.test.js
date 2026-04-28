const test = require("node:test");
const assert = require("node:assert/strict");

const {
  createSpy,
  createWxMock,
  loadPage,
  mockModule,
  clearModule
} = require("./helpers/test-utils");

function immediateTimeout() {
  const original = global.setTimeout;
  global.setTimeout = (fn) => {
    fn();
    return 1;
  };
  return () => {
    global.setTimeout = original;
  };
}

test("login page trims email input", () => {
  createWxMock();
  const page = loadPage("pages/login/login.js");

  page.onEmailInput({ detail: { value: "  bird@example.com  " } });

  assert.equal(page.data.email, "bird@example.com");
});

test("login page blocks submit when fields are missing", async () => {
  const { wx } = createWxMock();
  const restoreApi = mockModule("src/api/index.js", {
    auth: { login: createSpy(async () => ({})) }
  });

  const page = loadPage("pages/login/login.js");
  await page.onSignIn();

  assert.equal(wx.showToast.calls.length, 1);
  assert.deepEqual(wx.showToast.calls[0][0], {
    title: "Please complete all fields",
    icon: "none"
  });

  restoreApi();
});

test("login page validates email before calling auth api", async () => {
  const { wx } = createWxMock();
  const loginSpy = createSpy(async () => ({}));
  const restoreApi = mockModule("src/api/index.js", {
    auth: { login: loginSpy }
  });

  const page = loadPage("pages/login/login.js");
  page.setData({
    email: "invalid-email",
    password: "12345678"
  });

  await page.onSignIn();

  assert.equal(loginSpy.calls.length, 0);
  assert.equal(wx.showToast.calls[0][0].title, "Please enter a valid email");

  restoreApi();
});

test("login page submits successfully and redirects to index", async () => {
  const { wx } = createWxMock();
  const loginSpy = createSpy(async () => ({ code: 0 }));
  const restoreApi = mockModule("src/api/index.js", {
    auth: { login: loginSpy }
  });
  const restoreTimeout = immediateTimeout();

  const page = loadPage("pages/login/login.js");
  page.setData({
    email: "bird@example.com",
    password: "12345678"
  });

  await page.onSignIn();

  assert.equal(loginSpy.calls.length, 1);
  assert.deepEqual(loginSpy.calls[0][0], {
    email: "bird@example.com",
    password: "12345678"
  });
  assert.equal(wx.switchTab.calls.length, 1);
  assert.equal(wx.switchTab.calls[0][0].url, "/pages/index/index");
  assert.equal(page.data.loading, false);

  restoreTimeout();
  restoreApi();
});

test("register page input trims normal fields and preserves passwords", () => {
  createWxMock();
  const page = loadPage("pages/register/register.js");

  page.onInput({
    currentTarget: { dataset: { key: "fullName" } },
    detail: { value: "  邱志翔  " }
  });
  page.onInput({
    currentTarget: { dataset: { key: "password" } },
    detail: { value: " 12345678 " }
  });

  assert.equal(page.data.fullName, "邱志翔");
  assert.equal(page.data.password, " 12345678 ");
});

test("register page rejects mismatched passwords", async () => {
  const { wx } = createWxMock();
  const registerSpy = createSpy(async () => ({}));
  const restoreApi = mockModule("src/api/index.js", {
    auth: { register: registerSpy }
  });

  const page = loadPage("pages/register/register.js");
  page.setData({
    fullName: "邱志翔",
    email: "bird@example.com",
    password: "12345678",
    confirmPassword: "87654321"
  });

  await page.onSignUp();

  assert.equal(registerSpy.calls.length, 0);
  assert.equal(wx.showToast.calls[0][0].title, "Passwords do not match");

  restoreApi();
});

test("register page saves draft profile and redirects after successful signup", async () => {
  const { wx, storage } = createWxMock();
  const registerSpy = createSpy(async () => ({ code: 0 }));
  const restoreApi = mockModule("src/api/index.js", {
    auth: { register: registerSpy }
  });
  const restoreTimeout = immediateTimeout();

  const page = loadPage("pages/register/register.js");
  page.setData({
    fullName: "邱志翔",
    mobile: "13800138000",
    email: "bird@example.com",
    password: "12345678",
    confirmPassword: "12345678"
  });

  await page.onSignUp();

  assert.equal(registerSpy.calls.length, 1);
  assert.deepEqual(registerSpy.calls[0][0], {
    username: "邱志翔",
    email: "bird@example.com",
    password: "12345678"
  });
  assert.deepEqual(storage.get("profileDraft"), {
    username: "邱志翔",
    phone: "13800138000",
    email: "bird@example.com",
    password: "12345678",
    confirmPassword: "12345678",
    avatarUrl: ""
  });
  assert.equal(wx.redirectTo.calls.length, 1);
  assert.equal(wx.redirectTo.calls[0][0].url, "/pages/login/login");

  restoreTimeout();
  restoreApi();
});

test("community page updates AI button text from draft content", () => {
  createWxMock();
  const page = loadPage("pages/community/community.js");

  page.onDraftInput({ detail: { value: "已经有文案了" } });

  assert.equal(page.data.draftContent, "已经有文案了");
  assert.equal(page.data.draftAiButtonText, "AI Polish");
});

test("community page blocks AI generation when no image is selected", async () => {
  const { wx } = createWxMock();
  const authModule = require("../../utils/auth");
  const originalRequireAuth = authModule.requireAuth;
  authModule.requireAuth = () => true;

  const page = loadPage("pages/community/community.js");
  await page.onGenerateAICopy();

  assert.equal(wx.showToast.calls[0][0].title, "Please add a photo first");

  authModule.requireAuth = originalRequireAuth;
});

test("community page uploads local image before requesting AI copy", async () => {
  const { wx } = createWxMock();
  const authModule = require("../../utils/auth");
  const originalRequireAuth = authModule.requireAuth;
  authModule.requireAuth = () => true;

  const postsMock = {
    uploadImage: createSpy(async () => ({
      code: 0,
      data: { imageUrl: "/uploads/post_001.jpg" }
    })),
    aiCopywriting: createSpy(async () => ({
      code: 0,
      data: {
        content: "AI generated copy"
      }
    })),
    list: createSpy(async () => ({
      code: 0,
      data: { list: [], total: 0, page: 1, pageSize: 30 }
    }))
  };
  const restoreApi = mockModule("src/api/index.js", {
    posts: postsMock,
    users: { getCurrentUser: createSpy(async () => ({ data: { id: 1 } })) }
  });

  const page = loadPage("pages/community/community.js");
  page.setData({
    draftImages: ["wxfile://draft-image.jpg"],
    draftContent: ""
  });

  await page.onGenerateAICopy();

  assert.equal(postsMock.uploadImage.calls.length, 1);
  assert.equal(postsMock.uploadImage.calls[0][0], "wxfile://draft-image.jpg");
  assert.deepEqual(postsMock.aiCopywriting.calls[0][0], {
    mode: "generate",
    imageUrl: "/uploads/post_001.jpg",
    content: ""
  });
  assert.equal(page.data.draftContent, "AI generated copy");
  assert.equal(page.data.draftImages[0], "http://192.168.1.100:8000/uploads/post_001.jpg");
  assert.equal(page.data.draftAiButtonText, "AI Polish");
  assert.equal(page.data.aiCopyLoading, false);
  assert.equal(wx.showToast.calls[0][0].icon, "success");

  restoreApi();
  authModule.requireAuth = originalRequireAuth;
});

test("community page requires content before submitting a post", async () => {
  const { wx } = createWxMock();
  const authModule = require("../../utils/auth");
  const originalRequireAuth = authModule.requireAuth;
  authModule.requireAuth = () => true;

  const page = loadPage("pages/community/community.js");
  await page.onSubmitPost();

  assert.equal(wx.showToast.calls[0][0].title, "Please enter content");

  authModule.requireAuth = originalRequireAuth;
});

test("recognize page formats stored result on show", () => {
  createWxMock({
    initialStorage: {
      latestRecognizeResult: {
        birdName: "戴胜",
        confidence: 0.91,
        imageUrl: "/uploads/record_001.jpg",
        createdAt: "2026-04-21T08:30:00Z"
      }
    }
  });

  const page = loadPage("pages/recognize/recognize.js");
  page.onShow();

  assert.equal(page.data.result.birdName, "戴胜");
  assert.equal(page.data.result.confidenceText, "91%");
  assert.equal(page.data.result.fullImageUrl, "http://192.168.1.100:8000/uploads/record_001.jpg");
});

test("recognize page posts recognition result to community", async () => {
  const { wx } = createWxMock();
  const authModule = require("../../utils/auth");
  const originalRequireAuth = authModule.requireAuth;
  authModule.requireAuth = () => true;

  const createPostSpy = createSpy(async () => ({ code: 0 }));
  const restoreApi = mockModule("src/api/index.js", {
    posts: {
      create: createPostSpy
    }
  });

  const page = loadPage("pages/recognize/recognize.js");
  page.setData({
    result: {
      birdName: "戴胜",
      confidenceText: "91%",
      imageUrl: "/uploads/record_001.jpg"
    }
  });

  await page.onPostToCommunity();

  assert.equal(createPostSpy.calls.length, 1);
  assert.deepEqual(createPostSpy.calls[0][0], {
    content: "今天识别到：戴胜（置信度 91%）",
    imageUrl: "/uploads/record_001.jpg"
  });
  assert.equal(wx.showToast.calls[0][0].icon, "success");
  assert.equal(page.data.loadingPost, false);

  restoreApi();
  authModule.requireAuth = originalRequireAuth;
});

test.afterEach(() => {
  delete global.wx;
  delete global.Page;
  clearModule("pages/login/login.js");
  clearModule("pages/register/register.js");
  clearModule("pages/community/community.js");
  clearModule("pages/recognize/recognize.js");
});

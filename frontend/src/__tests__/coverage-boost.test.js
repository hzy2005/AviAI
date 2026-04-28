const test = require("node:test");
const assert = require("node:assert/strict");

const {
  createSpy,
  createWxMock,
  loadPage,
  mockModule,
  clearModule
} = require("./helpers/test-utils");

function useImmediateTimeout() {
  const original = global.setTimeout;
  global.setTimeout = (fn) => {
    fn();
    return 1;
  };
  return () => {
    global.setTimeout = original;
  };
}

function makeCommunityPage(options = {}) {
  const {
    requireAuthValue = true,
    postsMock = {},
    usersMock = {}
  } = options;
  const authModule = require("../../utils/auth");
  const originalRequireAuth = authModule.requireAuth;
  authModule.requireAuth = () => requireAuthValue;

  const restoreApi = mockModule("src/api/index.js", {
    posts: {
      list: createSpy(async () => ({ code: 0, data: { list: [], total: 0, page: 1, pageSize: 30 } })),
      uploadImage: createSpy(async () => ({ code: 0, data: { imageUrl: "/uploads/mock.jpg" } })),
      aiCopywriting: createSpy(async () => ({ code: 0, data: { content: "AI content" } })),
      create: createSpy(async () => ({ code: 0 })),
      update: createSpy(async () => ({ code: 0 })),
      remove: createSpy(async () => ({ code: 0 })),
      ...postsMock
    },
    users: {
      getCurrentUser: createSpy(async () => ({ data: { id: 1 } })),
      ...usersMock
    }
  });

  const page = loadPage("pages/community/community.js");

  return {
    page,
    restore() {
      restoreApi();
      authModule.requireAuth = originalRequireAuth;
    }
  };
}

test("community page onShow delegates to current-user and load flows", () => {
  createWxMock();
  const { page, restore } = makeCommunityPage();
  page.tryLoadCurrentUser = createSpy();
  page.resetAndLoad = createSpy();

  page.onShow();

  assert.equal(page.tryLoadCurrentUser.calls.length, 1);
  assert.equal(page.resetAndLoad.calls.length, 1);
  restore();
});

test("community page pull-down refresh stops spinner after reload", async () => {
  const { wx } = createWxMock();
  const { page, restore } = makeCommunityPage();
  page.resetAndLoad = createSpy(async () => {});

  await page.onPullDownRefresh();

  assert.equal(page.resetAndLoad.calls.length, 1);
  assert.equal(wx.stopPullDownRefresh.calls.length, 1);
  restore();
});

test("community page only loads more when reach-bottom is available", () => {
  createWxMock();
  const { page, restore } = makeCommunityPage();
  page.loadPosts = createSpy();

  page.setData({ noMore: false, loading: false });
  page.onReachBottom();
  page.setData({ noMore: true, loading: false });
  page.onReachBottom();
  page.setData({ noMore: false, loading: true });
  page.onReachBottom();

  assert.equal(page.loadPosts.calls.length, 1);
  restore();
});

test("community page builds feed columns and derives my posts", () => {
  createWxMock();
  const { page, restore } = makeCommunityPage();
  const feed = page.buildFeed([
    { postId: 1 },
    { postId: 2 },
    { postId: 3 },
    { postId: 4 }
  ]);

  page.setData({ currentUserId: 2 });
  const mine = page.deriveMyPosts([
    { postId: 1, author: { id: 1 } },
    { postId: 2, author: { id: 2 } },
    { postId: 3, author: null }
  ]);

  assert.deepEqual(feed.leftFeed.map((item) => item.sizeClass), ["large", "tall"]);
  assert.deepEqual(feed.rightFeed.map((item) => item.sizeClass), ["medium", "medium"]);
  assert.deepEqual(mine.map((item) => item.postId), [2]);
  restore();
});

test("community page tryLoadCurrentUser falls back when not logged in", async () => {
  createWxMock();
  const { page, restore } = makeCommunityPage();

  await page.tryLoadCurrentUser();

  assert.equal(page.data.currentUserId, null);
  restore();
});

test("community page tryLoadCurrentUser prefers API user and falls back to brief cache", async () => {
  createWxMock({
    initialStorage: {
      accessToken: "token",
      userBrief: { id: 7 }
    }
  });
  const { page, restore } = makeCommunityPage({
    usersMock: {
      getCurrentUser: createSpy(async () => ({ data: { id: 9 } }))
    }
  });
  page.setData({
    posts: [{ postId: 11, author: { id: 9 } }, { postId: 12, author: { id: 7 } }]
  });

  await page.tryLoadCurrentUser();

  assert.equal(page.data.currentUserId, 9);
  assert.deepEqual(page.data.myPosts.map((item) => item.postId), [12]);
  restore();
});

test("community page tryLoadCurrentUser falls back to brief cache on API failure", async () => {
  createWxMock({
    initialStorage: {
      accessToken: "token",
      userBrief: { id: 7 }
    }
  });
  const { page, restore } = makeCommunityPage({
    usersMock: {
      getCurrentUser: createSpy(async () => {
        throw new Error("fail");
      })
    }
  });
  page.setData({
    posts: [{ postId: 21, author: { id: 7 } }]
  });

  await page.tryLoadCurrentUser();

  assert.equal(page.data.currentUserId, 7);
  assert.deepEqual(page.data.myPosts.map((item) => item.postId), [21]);
  restore();
});

test("community page resetAndLoad keeps loading until enough cards are present", async () => {
  createWxMock();
  const { page, restore } = makeCommunityPage();
  let count = 0;
  page.loadPosts = createSpy(async () => {
    count += 1;
    page.setData({
      posts: new Array(count === 1 ? 5 : 12).fill({}),
      noMore: false
    });
  });

  await page.resetAndLoad();

  assert.equal(page.loadPosts.calls.length, 2);
  assert.equal(page.data.posts.length, 12);
  restore();
});

test("community page loadPosts maps API fields for display", async () => {
  createWxMock();
  const { page, restore } = makeCommunityPage({
    postsMock: {
      list: createSpy(async () => ({
        code: 0,
        data: {
          total: 2,
          list: [
            {
              postId: 1,
              content: "",
              imageUrl: "/uploads/a.jpg",
              likeCount: 0,
              createdAt: "2026-04-20T08:00:00Z",
              author: { id: 1 }
            },
            {
              postId: 2,
              content: "This is a very long post content that should be trimmed for the card title.",
              imageUrl: "/uploads/b.jpg",
              likeCount: 9,
              createdAt: "2026-04-20T09:00:00Z",
              author: { id: 2 }
            }
          ]
        }
      }))
    }
  });
  page.setData({ currentUserId: 1 });

  await page.loadPosts();

  assert.equal(page.data.posts.length, 2);
  assert.equal(page.data.posts[0].displayTitle, "Bird Story");
  assert.equal(page.data.posts[0].viewsText, "1 Views");
  assert.match(page.data.posts[1].displayTitle, /\.\.\.$/);
  assert.equal(page.data.myPosts.length, 1);
  assert.equal(page.data.leftFeed.length, 1);
  assert.equal(page.data.rightFeed.length, 1);
  assert.equal(page.data.noMore, true);
  restore();
});

test("community page loadPosts shows toast on API failure", async () => {
  const { wx } = createWxMock();
  const { page, restore } = makeCommunityPage({
    postsMock: {
      list: createSpy(async () => {
        throw new Error("Load failed");
      })
    }
  });

  await page.loadPosts();

  assert.equal(wx.showToast.calls.length, 1);
  assert.equal(page.data.loading, false);
  restore();
});

test("community page detail and preview helpers use wx APIs", () => {
  const { wx, storage } = createWxMock();
  const { page, restore } = makeCommunityPage();
  page.setData({
    posts: [{ postId: 99, content: "demo" }]
  });

  page.onOpenDetail({ currentTarget: { dataset: { id: 99 } } });
  page.onPreviewImage({ currentTarget: { dataset: { src: "http://img" } } });
  page.onPreviewImage({ currentTarget: { dataset: { src: "" } } });

  assert.deepEqual(storage.get("community-detail-prefetch-99"), { postId: 99, content: "demo" });
  assert.equal(wx.navigateTo.calls[0][0].url, "/pages/community-detail/community-detail?postId=99");
  assert.equal(wx.previewImage.calls.length, 1);
  restore();
});

test("community page search modal updates keyword and resets data", () => {
  createWxMock();
  const { page, restore } = makeCommunityPage();
  page.resetAndLoad = createSpy();

  page.onTapSearch();
  page.onSearchInput({ detail: { value: "  hoopoe  " } });
  page.onApplySearch();
  page.onClearSearch();

  assert.equal(page.data.showMask, true);
  assert.equal(page.resetAndLoad.calls.length, 2);
  assert.equal(page.data.keyword, "");
  assert.equal(page.data.searchInput, "");
  restore();
});

test("community page create and manage modals respect auth gate", () => {
  createWxMock();
  const denied = makeCommunityPage({ requireAuthValue: false });

  denied.page.onOpenCreateModal();
  denied.page.onOpenManageModal();
  assert.equal(denied.page.data.showCreateModal, false);
  assert.equal(denied.page.data.showManageModal, false);
  denied.restore();

  const allowed = makeCommunityPage({ requireAuthValue: true });
  allowed.page.setData({ draftContent: "draft text" });
  allowed.page.onOpenCreateModal();
  allowed.page.onOpenManageModal();
  allowed.page.onCloseModal();

  assert.equal(allowed.page.data.showSearch, false);
  assert.equal(allowed.page.data.showCreateModal, false);
  assert.equal(allowed.page.data.showManageModal, false);
  assert.equal(allowed.page.data.showMask, false);
  allowed.restore();
});

test("community page chooses, removes and limits draft images", async () => {
  createWxMock({
    chooseMedia: createSpy(({ success }) => {
      success({
        tempFiles: new Array(10).fill(0).map((_, index) => ({
          tempFilePath: `wxfile://draft-${index}.jpg`
        }))
      });
    })
  });
  const { page, restore } = makeCommunityPage();

  await page.onChooseDraftImages();
  page.onRemoveDraftImage({ currentTarget: { dataset: { index: 1 } } });

  assert.equal(page.data.draftImages.length, 8);
  assert.equal(page.data.draftImages[0], "wxfile://draft-0.jpg");
  restore();
});

test("community page ignores cancel and reports choose-image errors", async () => {
  const { wx } = createWxMock({
    chooseMedia: createSpy(({ fail }) => fail({ errMsg: "chooseMedia:fail cancel" }))
  });
  const first = makeCommunityPage();
  await first.page.onChooseDraftImages();
  assert.equal(wx.showToast.calls.length, 0);
  first.restore();

  wx.chooseMedia = createSpy(({ fail }) => fail({ errMsg: "chooseMedia:fail denied" }));
  const second = makeCommunityPage();
  await second.page.onChooseDraftImages();
  assert.equal(wx.showToast.calls.length, 1);
  second.restore();
});

test("community page upload helpers handle remote, local and invalid upload results", async () => {
  createWxMock();
  const { page, restore } = makeCommunityPage({
    postsMock: {
      uploadImage: createSpy(async () => ({ code: 0, data: { imageUrl: "/uploads/local.jpg" } }))
    }
  });

  page.setData({ draftImages: ["http://192.168.1.100:8000/uploads/existing.jpg"] });
  assert.equal(await page.ensureDraftImageUploaded(), "/uploads/existing.jpg");

  page.setData({ draftImages: ["wxfile://local.jpg"] });
  assert.equal(await page.ensureDraftImageUploaded(), "/uploads/local.jpg");
  assert.equal(page.data.draftImages[0], "http://192.168.1.100:8000/uploads/local.jpg");

  page.setData({ editingImages: ["tmp/edit.jpg"] });
  assert.equal(await page.ensureEditingImageUploaded(), "/uploads/local.jpg");

  const authModule = require("../../utils/auth");
  const originalRequireAuth = authModule.requireAuth;
  authModule.requireAuth = () => true;
  const restoreBrokenApi = mockModule("src/api/index.js", {
    posts: {
      uploadImage: createSpy(async () => ({ code: 0, data: {} }))
    },
    users: {
      getCurrentUser: createSpy(async () => ({ data: { id: 1 } }))
    }
  });
  const pageBroken = loadPage("pages/community/community.js");
  pageBroken.setData({ draftImages: ["wxfile://broken.jpg"] });
  await assert.rejects(() => pageBroken.ensureDraftImageUploaded(), /Image upload failed/);
  restoreBrokenApi();
  authModule.requireAuth = originalRequireAuth;
  restore();
});

test("community page generates AI copy in polish mode and handles failures", async () => {
  const { wx } = createWxMock();
  const success = makeCommunityPage({
    postsMock: {
      aiCopywriting: createSpy(async () => ({ code: 0, data: { content: "Polished copy" } }))
    }
  });
  success.page.setData({
    draftImages: ["http://192.168.1.100:8000/uploads/polish.jpg"],
    draftContent: "Need polish"
  });

  await success.page.onGenerateAICopy();

  assert.equal(success.page.data.draftContent, "Polished copy");
  assert.equal(success.page.data.aiCopyLoading, false);
  success.restore();

  const failure = makeCommunityPage({
    postsMock: {
      aiCopywriting: createSpy(async () => {
        throw new Error("AI copy failed");
      })
    }
  });
  failure.page.setData({
    draftImages: ["http://192.168.1.100:8000/uploads/polish.jpg"],
    draftContent: "Need polish"
  });

  await failure.page.onGenerateAICopy();

  assert.equal(wx.showToast.calls.at(-1)[0].icon, "none");
  failure.restore();
});

test("community page submits post and resets compose modal", async () => {
  const { wx } = createWxMock();
  const { page, restore } = makeCommunityPage({
    postsMock: {
      create: createSpy(async () => ({ code: 0 }))
    }
  });
  page.ensureDraftImageUploaded = createSpy(async () => "/uploads/post.jpg");
  page.resetAndLoad = createSpy(async () => {});
  page.setData({
    draftContent: "publish text",
    draftImages: ["wxfile://draft.jpg"],
    showCreateModal: true,
    showMask: true
  });

  await page.onSubmitPost();

  assert.equal(page.resetAndLoad.calls.length, 1);
  assert.equal(page.data.draftContent, "");
  assert.equal(page.data.showCreateModal, false);
  assert.equal(page.data.showMask, false);
  assert.equal(wx.showToast.calls.at(-1)[0].icon, "success");
  restore();
});

test("community page edit flow covers start, input, cancel and save branches", async () => {
  const { wx } = createWxMock();
  const { page, restore } = makeCommunityPage({
    postsMock: {
      update: createSpy(async () => ({ code: 0 }))
    }
  });
  page.setData({
    myPosts: [{ postId: 10, content: "old", fullImageUrl: "http://img/old.jpg" }]
  });

  page.onEditStart({ currentTarget: { dataset: { id: 10 } } });
  page.onEditInput({ detail: { value: "new text" } });
  page.onEditCancel();
  page.onEditStart({ currentTarget: { dataset: { id: 10 } } });
  page.ensureEditingImageUploaded = createSpy(async () => "/uploads/edited.jpg");
  page.resetAndLoad = createSpy(async () => {});

  await page.onEditSave({ currentTarget: { dataset: { id: 10 } } });

  assert.equal(page.resetAndLoad.calls.length, 1);
  assert.equal(page.data.editingPostId, null);
  assert.equal(wx.showToast.calls.at(-1)[0].icon, "success");

  page.setData({ editingContent: "   " });
  await page.onEditSave({ currentTarget: { dataset: { id: 10 } } });
  assert.equal(wx.showToast.calls.at(-1)[0].icon, "none");
  restore();
});

test("community page choose and remove edit images", async () => {
  createWxMock({
    chooseMedia: createSpy(({ success }) => {
      success({
        tempFiles: [{ tempFilePath: "wxfile://edit.jpg" }]
      });
    })
  });
  const { page, restore } = makeCommunityPage();

  await page.onChooseEditImages();
  page.onRemoveEditImage({ currentTarget: { dataset: { index: 0 } } });

  assert.equal(page.data.editingImages.length, 0);
  restore();
});

test("community page delete flow respects confirm, success and failure", async () => {
  const { wx } = createWxMock();
  const success = makeCommunityPage({
    postsMock: {
      remove: createSpy(async () => ({ code: 0 }))
    }
  });
  success.page.resetAndLoad = createSpy(async () => {});

  success.page.onDeletePost({ currentTarget: { dataset: { id: 10 } } });
  await wx.showModal.calls[0][0].success({ confirm: false });
  assert.equal(success.page.resetAndLoad.calls.length, 0);
  await wx.showModal.calls[0][0].success({ confirm: true });
  assert.equal(success.page.resetAndLoad.calls.length, 1);
  success.restore();

  const failure = makeCommunityPage({
    postsMock: {
      remove: createSpy(async () => {
        throw new Error("Delete failed");
      })
    }
  });
  failure.page.onDeletePost({ currentTarget: { dataset: { id: 11 } } });
  await wx.showModal.calls.at(-1)[0].success({ confirm: true });
  assert.equal(wx.showToast.calls.at(-1)[0].icon, "none");
  failure.restore();
});

test("request helper supports mock-first, success, failure and fallback paths", async () => {
  const { wx } = createWxMock({
    initialStorage: {
      accessToken: "token-1"
    },
    request: createSpy(({ success }) => {
      success({
        statusCode: 200,
        data: { code: 0, data: { ok: true } }
      });
    })
  });
  const restoreEnv = mockModule("config/env.js", {
    baseUrl: "http://api.example.com",
    enableOfflineMock: false,
    preferOfflineMock: false
  });
  clearModule("utils/request.js");
  const requestModule = require("../../utils/request");

  const successResult = await requestModule.request({
    url: "/api/v1/posts",
    method: "post",
    data: { id: 1 },
    header: { "X-Test": "1" }
  });

  assert.deepEqual(successResult, { code: 0, data: { ok: true } });
  assert.equal(wx.request.calls[0][0].url, "http://api.example.com/api/v1/posts");
  assert.equal(wx.request.calls[0][0].header.Authorization, "Bearer token-1");
  assert.equal(wx.request.calls[0][0].header["X-Test"], "1");

  restoreEnv();
});

test("request helper rejects API errors and raw request failures", async () => {
  createWxMock({
    request: createSpy(({ success }) => {
      success({
        statusCode: 401,
        data: { code: 1002, message: "bad" }
      });
    })
  });
  const restoreEnv = mockModule("config/env.js", {
    baseUrl: "http://api.example.com",
    enableOfflineMock: false,
    preferOfflineMock: false
  });
  clearModule("utils/request.js");
  let requestModule = require("../../utils/request");
  await assert.rejects(
    requestModule.request({ url: "/api/v1/users/me" }),
    (error) => error.statusCode === 401 && error.code === 1002
  );

  restoreEnv();
  createWxMock({
    request: createSpy(({ fail }) => fail({ errMsg: "boom" }))
  });
  const restoreEnv2 = mockModule("config/env.js", {
    baseUrl: "http://api.example.com",
    enableOfflineMock: false,
    preferOfflineMock: false
  });
  clearModule("utils/request.js");
  requestModule = require("../../utils/request");
  await assert.rejects(
    requestModule.request({ url: "/api/v1/users/me" }),
    (error) => error.errMsg === "boom"
  );
  restoreEnv2();
});

test("request helper uses offline mock and network fallback behavior", async () => {
  createWxMock({
    request: createSpy(({ fail }) => fail({ errMsg: "request:fail timeout" }))
  });
  const restoreEnv = mockModule("config/env.js", {
    baseUrl: "http://api.example.com",
    enableOfflineMock: true,
    preferOfflineMock: true
  });
  const restoreMockApi = mockModule("utils/mock-api.js", {
    getMockResponse: createSpy(() => ({ code: 0, data: { source: "mock" } }))
  });
  clearModule("utils/request.js");
  let requestModule = require("../../utils/request");

  const mockFirst = await requestModule.request({ url: "/api/v1/health" });
  assert.equal(mockFirst.data.source, "mock");

  restoreEnv();
  restoreMockApi();

  createWxMock({
    request: createSpy(({ fail }) => fail({ errMsg: "request:fail timeout" }))
  });
  const restoreEnv2 = mockModule("config/env.js", {
    baseUrl: "http://api.example.com",
    enableOfflineMock: true,
    preferOfflineMock: false
  });
  const restoreMockApi2 = mockModule("utils/mock-api.js", {
    getMockResponse: createSpy(() => ({ code: 0, data: { source: "fallback" } }))
  });
  clearModule("utils/request.js");
  requestModule = require("../../utils/request");
  const fallback = await requestModule.request({ url: "/api/v1/health" });
  assert.equal(fallback.data.source, "fallback");

  restoreEnv2();
  restoreMockApi2();

  createWxMock({
    request: createSpy(({ fail }) => fail({ errMsg: "request:fail timeout" }))
  });
  const restoreEnv3 = mockModule("config/env.js", {
    baseUrl: "http://api.example.com",
    enableOfflineMock: false,
    preferOfflineMock: false
  });
  clearModule("utils/request.js");
  requestModule = require("../../utils/request");
  let error = null;
  try {
    await requestModule.request({ url: "/api/v1/health" });
  } catch (caught) {
    error = caught;
  }
  assert.equal(requestModule.isNetworkError(error), true);
  restoreEnv3();
});

test("auth utility checks token and redirects unauthenticated users", () => {
  const restoreTimeout = useImmediateTimeout();
  const { wx } = createWxMock();
  clearModule("utils/auth.js");
  let authUtils = require("../../utils/auth");

  assert.equal(authUtils.hasToken(), false);
  assert.equal(authUtils.requireAuth({ redirect: false }), false);
  assert.equal(wx.showToast.calls.length, 1);

  wx.setStorageSync("accessToken", "token");
  clearModule("utils/auth.js");
  authUtils = require("../../utils/auth");
  assert.equal(authUtils.hasToken(), true);
  assert.equal(authUtils.requireAuth(), true);

  wx.removeStorageSync("accessToken");
  clearModule("utils/auth.js");
  authUtils = require("../../utils/auth");
  authUtils.requireAuth();
  assert.equal(wx.navigateTo.calls.length, 1);

  restoreTimeout();
});

test("posts API methods build expected request configs", async () => {
  createWxMock();
  const apiClientSpy = createSpy(async (config) => config);
  const restoreClient = mockModule("src/api/client.js", {
    apiClient: apiClientSpy
  });
  clearModule("src/api/posts.js");
  const posts = require("../api/posts");

  await posts.create({ content: "x" });
  await posts.aiCopywriting({ mode: "generate" });
  await posts.list({ page: 3, pageSize: 5, keyword: "owl bird" });
  await posts.detail(10);
  await posts.update(10, { content: "y" });
  await posts.remove(10);
  await posts.like(10);
  await posts.comment(10, { content: "nice" });

  assert.equal(apiClientSpy.calls.length, 8);
  assert.equal(apiClientSpy.calls[2][0].url, "/api/v1/posts?page=3&pageSize=5&keyword=owl%20bird");
  assert.equal(apiClientSpy.calls[4][0].method, "PUT");
  assert.equal(apiClientSpy.calls[5][0].method, "DELETE");
  assert.equal(apiClientSpy.calls[6][0].url, "/api/v1/posts/10/like");

  restoreClient();
});

test("mock API covers auth, posts and record flows", () => {
  const { storage } = createWxMock();
  clearModule("utils/mock-api.js");
  const { getMockResponse, getMockRecognizeResponse } = require("../../utils/mock-api");

  const health = getMockResponse({ url: "/api/v1/health", method: "GET" });
  assert.equal(health.code, 0);

  assert.equal(
    getMockResponse({
      url: "/api/v1/auth/register",
      method: "POST",
      data: { username: "", email: "bad", password: "123" }
    }).code,
    1001
  );

  const register = getMockResponse({
    url: "/api/v1/auth/register",
    method: "POST",
    data: { username: "newuser", email: "new@example.com", password: "12345678" }
  });
  assert.equal(register.code, 0);

  const login = getMockResponse({
    url: "/api/v1/auth/login",
    method: "POST",
    data: { email: "new@example.com", password: "12345678" }
  });
  assert.equal(login.code, 0);

  const me = getMockResponse({
    url: "/api/v1/users/me",
    method: "GET",
    token: "token"
  });
  assert.equal(me.data.username, "newuser");

  const record = getMockRecognizeResponse("/uploads/recognize.jpg");
  assert.equal(record.code, 0);

  const records = getMockResponse({
    url: "/api/v1/birds/records?page=1&pageSize=2",
    method: "GET",
    token: "token"
  });
  assert.equal(records.data.list.length, 2);

  const created = getMockResponse({
    url: "/api/v1/posts",
    method: "POST",
    token: "token",
    data: { content: "post body", imageUrl: "/uploads/p.jpg" }
  });
  assert.equal(created.code, 0);

  const detail = getMockResponse({
    url: `/api/v1/posts/${created.data.postId}`,
    method: "GET"
  });
  assert.equal(detail.data.content, "post body");

  const updated = getMockResponse({
    url: `/api/v1/posts/${created.data.postId}`,
    method: "PUT",
    token: "token",
    data: { content: "updated body", imageUrl: "" }
  });
  assert.equal(updated.code, 0);

  const like = getMockResponse({
    url: `/api/v1/posts/${created.data.postId}/like`,
    method: "POST",
    token: "token"
  });
  const comment = getMockResponse({
    url: `/api/v1/posts/${created.data.postId}/comments`,
    method: "POST",
    token: "token",
    data: { content: "nice" }
  });
  assert.equal(like.code, 0);
  assert.equal(comment.code, 0);

  const aiGenerate = getMockResponse({
    url: "/api/v1/posts/ai-copywriting",
    method: "POST",
    token: "token",
    data: { mode: "generate", imageUrl: "/uploads/p.jpg", content: "" }
  });
  const aiPolish = getMockResponse({
    url: "/api/v1/posts/ai-copywriting",
    method: "POST",
    token: "token",
    data: { mode: "polish", imageUrl: "/uploads/p.jpg", content: "draft" }
  });
  assert.equal(aiGenerate.code, 0);
  assert.equal(aiPolish.code, 0);

  const deleted = getMockResponse({
    url: `/api/v1/posts/${created.data.postId}`,
    method: "DELETE",
    token: "token"
  });
  assert.equal(deleted.code, 0);

  assert.equal(
    getMockResponse({
      url: `/api/v1/posts/${created.data.postId}`,
      method: "GET"
    }).code,
    1004
  );

  storage.clear();
});

test.afterEach(() => {
  delete global.wx;
  delete global.Page;
  clearModule("pages/community/community.js");
  clearModule("src/api/posts.js");
  clearModule("utils/request.js");
  clearModule("utils/auth.js");
  clearModule("utils/mock-api.js");
});

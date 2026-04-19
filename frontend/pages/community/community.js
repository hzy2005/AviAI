const { posts, users } = require("../../src/api/index");
const { requireAuth } = require("../../utils/auth");
const { formatDateTime, toFullImageUrl } = require("../../utils/format");

function chooseImageFiles() {
  return new Promise((resolve, reject) => {
    wx.chooseMedia({
      count: 9,
      mediaType: ["image"],
      sourceType: ["album", "camera"],
      success: resolve,
      fail: reject
    });
  });
}

function getCardSize(index) {
  const mod = index % 4;
  if (mod === 0) return "large";
  if (mod === 1) return "medium";
  if (mod === 2) return "tall";
  return "medium";
}

function getDisplayTitle(content) {
  const text = String(content || "").trim();
  if (!text) return "Bird Story";
  return text.length > 26 ? `${text.slice(0, 26)}...` : text;
}

function getDraftAiButtonText(content) {
  return String(content || "").trim() ? "AI Polish" : "AI Generate";
}

Page({
  data: {
    posts: [],
    leftFeed: [],
    rightFeed: [],
    myPosts: [],
    page: 1,
    pageSize: 30,
    total: 0,
    keyword: "",
    searchInput: "",
    loading: false,
    noMore: false,
    showSearch: false,
    showCreateModal: false,
    showManageModal: false,
    showMask: false,
    draftContent: "",
    draftImages: [],
    draftAiButtonText: "AI Generate",
    aiCopyLoading: false,
    submitting: false,
    editingPostId: null,
    editingContent: "",
    editingImages: [],
    currentUserId: null
  },

  onShow() {
    this.tryLoadCurrentUser();
    this.resetAndLoad();
  },

  onPullDownRefresh() {
    this.resetAndLoad().finally(() => wx.stopPullDownRefresh());
  },

  onReachBottom() {
    if (!this.data.noMore && !this.data.loading) {
      this.loadPosts();
    }
  },

  async tryLoadCurrentUser() {
    const token = wx.getStorageSync("accessToken");
    const brief = wx.getStorageSync("userBrief") || {};
    if (!token) {
      this.setData({ currentUserId: null });
      return;
    }

    if (brief.id) {
      this.setData({
        currentUserId: brief.id,
        myPosts: this.deriveMyPosts(this.data.posts)
      });
    }

    try {
      const res = await users.getCurrentUser();
      this.setData({
        currentUserId: res.data.id || null,
        myPosts: this.deriveMyPosts(this.data.posts)
      });
    } catch (error) {
      this.setData({
        currentUserId: brief.id || null,
        myPosts: this.deriveMyPosts(this.data.posts)
      });
    }
  },

  buildFeed(postsList) {
    const leftFeed = [];
    const rightFeed = [];

    postsList.forEach((item, index) => {
      const card = {
        ...item,
        sizeClass: getCardSize(index)
      };

      if (index % 2 === 0) {
        leftFeed.push(card);
      } else {
        rightFeed.push(card);
      }
    });

    return { leftFeed, rightFeed };
  },

  deriveMyPosts(allPosts) {
    const { currentUserId } = this.data;
    if (!currentUserId) {
      return [];
    }
    return allPosts.filter((item) => item.author && item.author.id === currentUserId);
  },

  async resetAndLoad() {
    this.setData({ posts: [], leftFeed: [], rightFeed: [], page: 1, total: 0, noMore: false });
    await this.loadPosts();

    // Keep loading by API pagination until the masonry has enough cards or no more data.
    while (!this.data.noMore && this.data.posts.length < 12) {
      await this.loadPosts();
    }
  },

  async loadPosts() {
    this.setData({ loading: true });

    try {
      const res = await posts.list({
        page: this.data.page,
        pageSize: this.data.pageSize,
        keyword: this.data.keyword
      });

      const incoming = (res.data.list || []).map((item, index) => ({
        ...item,
        feedIndex: this.data.posts.length + index,
        createdAtText: formatDateTime(item.createdAt),
        fullImageUrl: toFullImageUrl(item.imageUrl),
        displayTitle: getDisplayTitle(item.content),
        viewsText: `${Math.max(Number(item.likeCount) || 0, 1)} Views`
      }));

      const merged = [...this.data.posts, ...incoming];
      const total = res.data.total || 0;
      const { leftFeed, rightFeed } = this.buildFeed(merged);
      const myPosts = this.deriveMyPosts(merged);

      this.setData({
        posts: merged,
        leftFeed,
        rightFeed,
        myPosts,
        page: this.data.page + 1,
        total,
        noMore: merged.length >= total
      });
    } catch (error) {
      wx.showToast({ title: error.message || "Load failed", icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  },

  onOpenDetail(event) {
    const postId = Number(event.currentTarget.dataset.id);
    const post = this.data.posts.find((item) => Number(item.postId) === postId);
    if (post) {
      wx.setStorageSync(`community-detail-prefetch-${postId}`, post);
    }
    wx.navigateTo({ url: `/pages/community-detail/community-detail?postId=${postId}` });
  },

  onPreviewImage(event) {
    const src = event.currentTarget.dataset.src;
    if (!src) return;
    wx.previewImage({ urls: [src], current: src });
  },

  onTapSearch() {
    this.setData({
      showSearch: true,
      showCreateModal: false,
      showManageModal: false,
      showMask: true
    });
  },

  onSearchInput(event) {
    this.setData({ searchInput: event.detail.value });
  },

  onApplySearch() {
    this.setData({
      keyword: this.data.searchInput.trim(),
      showSearch: false
    });
    this.resetAndLoad();
  },

  onClearSearch() {
    this.setData({
      keyword: "",
      searchInput: "",
      showSearch: false
    });
    this.resetAndLoad();
  },

  onOpenCreateModal() {
    if (!requireAuth()) return;
    this.setData({
      showCreateModal: true,
      showManageModal: false,
      showSearch: false,
      showMask: true,
      draftAiButtonText: getDraftAiButtonText(this.data.draftContent)
    });
  },

  onOpenManageModal() {
    if (!requireAuth()) return;
    this.setData({
      showManageModal: true,
      showCreateModal: false,
      showSearch: false,
      showMask: true,
      editingPostId: null,
      editingContent: "",
      editingImages: []
    });
  },

  onCloseModal() {
    this.setData({
      showSearch: false,
      showCreateModal: false,
      showManageModal: false,
      showMask: false,
      aiCopyLoading: false,
      editingPostId: null,
      editingContent: "",
      editingImages: []
    });
  },

  onStopBubble() {},

  onDraftInput(event) {
    const draftContent = event.detail.value;
    this.setData({
      draftContent,
      draftAiButtonText: getDraftAiButtonText(draftContent)
    });
  },

  async onChooseDraftImages() {
    if (!requireAuth()) return;

    try {
      const chooseRes = await chooseImageFiles();
      const files = (chooseRes.tempFiles || [])
        .map((item) => item.tempFilePath)
        .filter(Boolean);
      if (!files.length) return;

      const merged = [...this.data.draftImages, ...files].slice(0, 9);
      this.setData({ draftImages: merged });
    } catch (error) {
      if (error && error.errMsg && error.errMsg.includes("cancel")) {
        return;
      }
      wx.showToast({ title: "Image choose failed", icon: "none" });
    }
  },

  onRemoveDraftImage(event) {
    const index = Number(event.currentTarget.dataset.index);
    const next = this.data.draftImages.filter((_, i) => i !== index);
    this.setData({ draftImages: next });
  },

  async onGenerateAICopy() {
    if (!requireAuth()) return;

    const imageUrl = this.data.draftImages[0] || "";
    const content = this.data.draftContent.trim();

    if (!imageUrl) {
      wx.showToast({ title: "Please add a photo first", icon: "none" });
      return;
    }

    const mode = content ? "polish" : "generate";

    try {
      this.setData({ aiCopyLoading: true });
      const res = await posts.aiCopywriting({
        mode,
        imageUrl,
        content
      });
      const nextContent = (res.data && res.data.content) || "";
      this.setData({
        draftContent: nextContent,
        draftAiButtonText: getDraftAiButtonText(nextContent)
      });
      wx.showToast({
        title: mode === "generate" ? "文案已生成" : "文案已润色",
        icon: "success"
      });
    } catch (error) {
      wx.showToast({ title: error.message || "AI copy failed", icon: "none" });
    } finally {
      this.setData({ aiCopyLoading: false });
    }
  },

  async onSubmitPost() {
    if (!requireAuth()) return;

    const content = this.data.draftContent.trim();
    if (!content) {
      wx.showToast({ title: "Please enter content", icon: "none" });
      return;
    }

    try {
      this.setData({ submitting: true });
      await posts.create({
        content,
        imageUrl: this.data.draftImages[0] || null
      });
      wx.showToast({ title: "Posted", icon: "success" });
      this.setData({
        draftContent: "",
        draftImages: [],
        draftAiButtonText: "AI Generate",
        aiCopyLoading: false,
        showCreateModal: false,
        showMask: false
      });
      await this.resetAndLoad();
    } catch (error) {
      wx.showToast({ title: error.message || "Publish failed", icon: "none" });
    } finally {
      this.setData({ submitting: false });
    }
  },

  onEditStart(event) {
    const postId = Number(event.currentTarget.dataset.id);
    const post = this.data.myPosts.find((item) => item.postId === postId);
    if (!post) return;

    this.setData({
      editingPostId: postId,
      editingContent: post.content || "",
      editingImages: post.fullImageUrl ? [post.fullImageUrl] : []
    });
  },

  onEditInput(event) {
    this.setData({ editingContent: event.detail.value });
  },

  onEditCancel() {
    this.setData({
      editingPostId: null,
      editingContent: "",
      editingImages: []
    });
  },

  async onChooseEditImages() {
    if (!requireAuth()) return;
    try {
      const chooseRes = await chooseImageFiles();
      const files = (chooseRes.tempFiles || [])
        .map((item) => item.tempFilePath)
        .filter(Boolean);
      if (!files.length) return;
      const merged = [...this.data.editingImages, ...files].slice(0, 9);
      this.setData({ editingImages: merged });
    } catch (error) {
      if (error && error.errMsg && error.errMsg.includes("cancel")) {
        return;
      }
      wx.showToast({ title: "Image choose failed", icon: "none" });
    }
  },

  onRemoveEditImage(event) {
    const index = Number(event.currentTarget.dataset.index);
    const next = this.data.editingImages.filter((_, i) => i !== index);
    this.setData({ editingImages: next });
  },

  async onEditSave(event) {
    const postId = Number(event.currentTarget.dataset.id);
    const content = this.data.editingContent.trim();

    if (!content) {
      wx.showToast({ title: "Content cannot be empty", icon: "none" });
      return;
    }

    try {
      await posts.update(postId, {
        content,
        imageUrl: this.data.editingImages[0] || null
      });
      wx.showToast({ title: "Updated", icon: "success" });
      this.setData({ editingPostId: null, editingContent: "", editingImages: [] });
      await this.resetAndLoad();
    } catch (error) {
      wx.showToast({ title: error.message || "Update failed", icon: "none" });
    }
  },

  async onDeletePost(event) {
    if (!requireAuth()) return;

    const postId = Number(event.currentTarget.dataset.id);
    if (!postId) return;

    wx.showModal({
      title: "Delete Post",
      content: "Are you sure you want to delete this post?",
      success: async (res) => {
        if (!res.confirm) return;
        try {
          await posts.remove(postId);
          wx.showToast({ title: "Deleted", icon: "success" });
          await this.resetAndLoad();
        } catch (error) {
          wx.showToast({ title: error.message || "Delete failed", icon: "none" });
        }
      }
    });
  }
});

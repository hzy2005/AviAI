const { posts } = require("../../src/api/index");
const { requireAuth } = require("../../utils/auth");
const { formatDateTime, toFullImageUrl } = require("../../utils/format");

const DEFAULT_AVATAR = "/static/icons/icon-user.png";
const ICON_BACK = "/static/icons/return.png";
const ICON_LIKE = "/static/icons/like.png";
const ICON_COMMENT = "/static/icons/comments.png";
const ICON_SHARE = "/static/icons/share.png";

function getCommentKey(postId) {
  return `post-comments-${postId}`;
}

function getLikeKey(postId) {
  return `post-liked-${postId}`;
}

function normalizeComment(raw = {}) {
  const commentId = Number(raw.commentId || raw.id || Date.now());
  return {
    commentId,
    postId: Number(raw.postId || 0),
    userId: Number(raw.userId || 0),
    username: raw.username || "User",
    avatarUrl: raw.avatarUrl || "",
    content: raw.content || "",
    parentId: raw.parentId == null ? null : Number(raw.parentId),
    imageUrls: Array.isArray(raw.imageUrls) ? raw.imageUrls : [],
    createdAt: raw.createdAt || new Date().toISOString(),
    createdAtText: raw.createdAtText || formatDateTime(raw.createdAt || Date.now())
  };
}

function parsePostContent(content) {
  const text = String(content || "").trim();
  if (!text) {
    return {
      title: "Bird Story",
      body: ""
    };
  }

  const lines = text.split(/\r?\n/);
  const title = (lines[0] || "").trim() || "Bird Story";
  const body = lines.slice(1).join("\n").trim() || text;

  return { title, body };
}

function normalizePostDetail(raw = {}) {
  const parsed = parsePostContent(raw.content);
  return {
    ...raw,
    postTitle: parsed.title,
    postBody: parsed.body,
    createdAtText: formatDateTime(raw.createdAt),
    fullImageUrl: toFullImageUrl(raw.imageUrl)
  };
}

function buildCommentTree(list) {
  const sorted = [...list].sort((a, b) => {
    const ta = new Date(a.createdAt).getTime();
    const tb = new Date(b.createdAt).getTime();
    return ta - tb;
  });

  const map = new Map();
  sorted.forEach((item) => {
    map.set(item.commentId, { ...item, replies: [] });
  });

  const roots = [];
  sorted.forEach((item) => {
    const node = map.get(item.commentId);
    if (item.parentId && map.has(item.parentId)) {
      map.get(item.parentId).replies.push(node);
      return;
    }
    roots.push(node);
  });

  return roots.reverse();
}

function chooseCommentImages() {
  return new Promise((resolve, reject) => {
    wx.chooseMedia({
      count: 3,
      mediaType: ["image"],
      sourceType: ["album", "camera"],
      success: resolve,
      fail: reject
    });
  });
}

Page({
  data: {
    statusBarHeight: 0,
    postId: "",
    detail: null,
    imageList: [],
    loading: false,
    showReadMore: false,
    isTalkExpanded: false,
    liked: false,
    displayLikeCount: 0,
    rawComments: [],
    commentTree: [],
    currentUserId: null,
    defaultAvatar: DEFAULT_AVATAR,
    iconBack: ICON_BACK,
    iconLike: ICON_LIKE,
    iconComment: ICON_COMMENT,
    iconShare: ICON_SHARE,
    showCommentModal: false,
    draftCommentText: "",
    draftCommentImages: [],
    replyTarget: null,
    submittingComment: false
  },

  onLoad(options) {
    const sys = wx.getSystemInfoSync();
    const postId = options.postId || "";
    const liked = Boolean(wx.getStorageSync(getLikeKey(postId)));
    const brief = wx.getStorageSync("userBrief") || {};

    this.setData({
      statusBarHeight: sys.statusBarHeight || 0,
      postId,
      liked,
      currentUserId: brief.id || null
    });

    this.applyPrefetchedDetail(postId);
    wx.showShareMenu({ withShareTicket: true, menus: ["shareAppMessage"] });

    this.loadLocalComments();
    this.loadDetail();
  },

  applyPrefetchedDetail(postId) {
    const cached = wx.getStorageSync(`community-detail-prefetch-${postId}`);
    if (!cached) {
      return;
    }

    const detail = normalizePostDetail(cached);
    const imageList = detail.fullImageUrl ? [detail.fullImageUrl] : [];

    this.setData({
      detail,
      imageList,
      displayLikeCount: Number(detail.likeCount || 0),
      showReadMore: String(detail.postBody || "").length > 120
    });
  },

  loadLocalComments() {
    const list = wx.getStorageSync(getCommentKey(this.data.postId)) || [];
    const normalized = list.map((item) => normalizeComment(item));
    this.setData({
      rawComments: normalized,
      commentTree: buildCommentTree(normalized)
    });
  },

  saveLocalComments(list) {
    wx.setStorageSync(getCommentKey(this.data.postId), list);
    this.setData({
      rawComments: list,
      commentTree: buildCommentTree(list)
    });
  },

  async loadDetail() {
    if (!this.data.postId) {
      return;
    }

    this.setData({ loading: true });
    try {
      const res = await posts.detail(this.data.postId);
      const detail = normalizePostDetail(res.data);

      const images = Array.isArray(res.data.imageUrls)
        ? res.data.imageUrls.map((url) => toFullImageUrl(url)).filter(Boolean)
        : [];

      const imageList = images.length
        ? images
        : (detail.fullImageUrl ? [detail.fullImageUrl] : []);

      this.setData({
        detail,
        imageList,
        displayLikeCount: Number(detail.likeCount || 0),
        showReadMore: String(detail.postBody || "").length > 120
      });
    } catch (error) {
      wx.showToast({ title: error.message || "Detail load failed", icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  },

  onBack() {
    if (getCurrentPages().length > 1) {
      wx.navigateBack();
      return;
    }
    wx.switchTab({ url: "/pages/community/community" });
  },

  onTapShare() {
    wx.showActionSheet({
      itemList: ["Share to chat", "Share to moments"],
      success: () => {
        wx.showToast({ title: "Use system share panel", icon: "none" });
      }
    });
  },

  onShareAppMessage() {
    const detail = this.data.detail || {};
    return {
      title: detail.postTitle || detail.content || "AviAI Community Post",
      path: `/pages/community-detail/community-detail?postId=${this.data.postId}`,
      imageUrl: this.data.imageList[0] || ""
    };
  },

  onPreviewImage(event) {
    const src = event.currentTarget.dataset.src;
    if (!src) return;
    wx.previewImage({ urls: this.data.imageList, current: src });
  },

  onPreviewCommentImage(event) {
    const src = event.currentTarget.dataset.src;
    if (!src) return;
    wx.previewImage({ urls: [src], current: src });
  },

  onToggleTalk() {
    this.setData({ isTalkExpanded: !this.data.isTalkExpanded });
  },

  async onLike() {
    if (!requireAuth()) {
      return;
    }

    if (this.data.liked) {
      wx.showToast({ title: "Already liked", icon: "none" });
      return;
    }

    try {
      await posts.like(this.data.postId);
      const nextCount = Number(this.data.displayLikeCount || 0) + 1;
      wx.setStorageSync(getLikeKey(this.data.postId), true);
      this.setData({
        liked: true,
        displayLikeCount: nextCount
      });
      wx.showToast({ title: "Liked", icon: "success" });
    } catch (error) {
      wx.showToast({ title: error.message || "Like failed", icon: "none" });
    }
  },

  onOpenCommentModal() {
    if (!requireAuth()) {
      return;
    }
    this.setData({
      showCommentModal: true,
      draftCommentText: "",
      draftCommentImages: [],
      replyTarget: null
    });
  },

  onCloseCommentModal() {
    this.setData({
      showCommentModal: false,
      draftCommentText: "",
      draftCommentImages: [],
      replyTarget: null,
      submittingComment: false
    });
  },

  onStopBubble() {},

  onReplyComment(event) {
    if (!requireAuth()) {
      return;
    }

    const commentId = Number(event.currentTarget.dataset.id);
    const username = event.currentTarget.dataset.username || "User";

    this.setData({
      showCommentModal: true,
      draftCommentText: "",
      draftCommentImages: [],
      replyTarget: {
        commentId,
        username
      }
    });
  },

  async onChooseCommentImages() {
    try {
      const chooseRes = await chooseCommentImages();
      const files = (chooseRes.tempFiles || []).map((item) => item.tempFilePath).filter(Boolean);
      if (!files.length) {
        return;
      }
      const merged = [...this.data.draftCommentImages, ...files].slice(0, 3);
      this.setData({ draftCommentImages: merged });
    } catch (error) {
      if (error && error.errMsg && error.errMsg.includes("cancel")) {
        return;
      }
      wx.showToast({ title: "Image choose failed", icon: "none" });
    }
  },

  onRemoveDraftCommentImage(event) {
    const index = Number(event.currentTarget.dataset.index);
    const next = this.data.draftCommentImages.filter((_, i) => i !== index);
    this.setData({ draftCommentImages: next });
  },

  onDraftCommentInput(event) {
    this.setData({ draftCommentText: event.detail.value });
  },

  async onSubmitComment() {
    if (!requireAuth()) {
      return;
    }

    const content = this.data.draftCommentText.trim();
    if (!content) {
      wx.showToast({ title: "Please enter comment", icon: "none" });
      return;
    }

    this.setData({ submittingComment: true });
    try {
      const parentId = this.data.replyTarget ? this.data.replyTarget.commentId : null;
      const res = await posts.comment(this.data.postId, {
        content,
        parentId
      });

      const now = Date.now();
      const user = wx.getStorageSync("userBrief") || {};
      const nextItem = normalizeComment({
        commentId: (res.data && res.data.commentId) || now,
        postId: Number(this.data.postId),
        userId: user.id || this.data.currentUserId || 0,
        username: user.username || "Me",
        avatarUrl: user.avatarUrl || "",
        content,
        parentId,
        imageUrls: this.data.draftCommentImages,
        createdAt: new Date(now).toISOString()
      });

      const nextList = [nextItem, ...this.data.rawComments];
      this.saveLocalComments(nextList);
      this.setData({
        showCommentModal: false,
        draftCommentText: "",
        draftCommentImages: [],
        replyTarget: null
      });

      const nextCount = Number(this.data.detail.commentCount || 0) + 1;
      this.setData({
        detail: {
          ...this.data.detail,
          commentCount: nextCount
        }
      });

      wx.showToast({ title: "Comment posted", icon: "success" });
    } catch (error) {
      wx.showToast({ title: error.message || "Comment failed", icon: "none" });
    } finally {
      this.setData({ submittingComment: false });
    }
  },

  onLongPressComment(event) {
    const commentId = Number(event.currentTarget.dataset.id);
    const userId = Number(event.currentTarget.dataset.userId || 0);

    if (!this.data.currentUserId || userId !== this.data.currentUserId) {
      return;
    }

    wx.showModal({
      title: "Delete Comment",
      content: "Delete this comment?",
      success: (res) => {
        if (!res.confirm) {
          return;
        }

        const idsToDelete = new Set([commentId]);
        this.data.rawComments.forEach((item) => {
          if (Number(item.parentId) === commentId) {
            idsToDelete.add(item.commentId);
          }
        });

        const nextList = this.data.rawComments.filter((item) => !idsToDelete.has(item.commentId));
        this.saveLocalComments(nextList);
        wx.showToast({ title: "Deleted", icon: "success" });
      }
    });
  }
});


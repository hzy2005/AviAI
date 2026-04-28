const path = require("path");

function createSpy(impl = () => {}) {
  const spy = function (...args) {
    spy.calls.push(args);
    return impl.apply(this, args);
  };

  spy.calls = [];
  return spy;
}

function resolveFromFrontend(relativePath) {
  return path.resolve(__dirname, "..", "..", "..", relativePath);
}

function clearModule(relativePath) {
  const resolved = require.resolve(resolveFromFrontend(relativePath));
  delete require.cache[resolved];
  return resolved;
}

function mockModule(relativePath, exports) {
  const resolved = require.resolve(resolveFromFrontend(relativePath));
  const previous = require.cache[resolved];
  require.cache[resolved] = {
    id: resolved,
    filename: resolved,
    loaded: true,
    exports
  };

  return () => {
    if (previous) {
      require.cache[resolved] = previous;
      return;
    }
    delete require.cache[resolved];
  };
}

function createWxMock(options = {}) {
  const { initialStorage = {}, ...overrides } = options;
  const storage = new Map(Object.entries(initialStorage));
  const fileState = new Map();

  const wxMock = {
    env: {
      USER_DATA_PATH: "/mock-user-data"
    },
    getStorageSync: createSpy((key) => storage.get(key)),
    setStorageSync: createSpy((key, value) => {
      storage.set(key, value);
    }),
    removeStorageSync: createSpy((key) => {
      storage.delete(key);
    }),
    showToast: createSpy(),
    navigateTo: createSpy(),
    redirectTo: createSpy(),
    switchTab: createSpy(),
    previewImage: createSpy(),
    stopPullDownRefresh: createSpy(),
    request: createSpy(),
    uploadFile: createSpy(),
    chooseMedia: createSpy(),
    showModal: createSpy(),
    getFileSystemManager: createSpy(() => ({
      readFileSync(filePath) {
        if (!fileState.has(filePath)) {
          throw new Error("ENOENT");
        }
        return fileState.get(filePath);
      },
      writeFileSync(filePath, content) {
        fileState.set(filePath, content);
      }
    })),
    ...overrides
  };

  global.wx = wxMock;
  return { wx: wxMock, storage, fileState };
}

function loadPage(relativePath) {
  let config = null;
  global.Page = (pageConfig) => {
    config = pageConfig;
  };

  clearModule(relativePath);
  require(resolveFromFrontend(relativePath));

  if (!config) {
    throw new Error(`Page was not registered for ${relativePath}`);
  }

  const page = {
    data: JSON.parse(JSON.stringify(config.data || {})),
    setData(update) {
      this.data = {
        ...this.data,
        ...update
      };
    }
  };

  Object.keys(config).forEach((key) => {
    if (key === "data") {
      return;
    }
    page[key] = typeof config[key] === "function" ? config[key].bind(page) : config[key];
  });

  return page;
}

module.exports = {
  createSpy,
  createWxMock,
  loadPage,
  mockModule,
  clearModule,
  resolveFromFrontend
};

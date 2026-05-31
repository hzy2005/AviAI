const isDevtools = typeof __wxConfig !== "undefined";

// Simulator can use localhost. Real device should use LAN IP.
const DEV_BASE_URL = "http://127.0.0.1:8000";
const LAN_BASE_URL = "http://192.168.1.100:8000";
const PROD_BASE_URL = "https://aviai-backend.onrender.com";
const USE_CLOUD_BACKEND = true;

const baseUrl = USE_CLOUD_BACKEND ? PROD_BASE_URL : isDevtools ? DEV_BASE_URL : LAN_BASE_URL;

// Temporary development mode:
// force all API calls to use local mock handlers first.
const enableOfflineMock = !USE_CLOUD_BACKEND;
const preferOfflineMock = false;

module.exports = {
  baseUrl,
  enableOfflineMock,
  preferOfflineMock,
  isDevtools,
  useCloudBackend: USE_CLOUD_BACKEND
};

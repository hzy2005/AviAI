const isDevtools = typeof __wxConfig !== "undefined";

// Simulator can use localhost. Real device should use LAN IP.
const DEV_BASE_URL = "http://127.0.0.1:8000";
const LAN_BASE_URL = "http://192.168.1.100:8000";

const baseUrl = isDevtools ? DEV_BASE_URL : LAN_BASE_URL;

module.exports = {
  baseUrl
};

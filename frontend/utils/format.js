const { baseUrl } = require("../config/env");

function formatDateTime(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  const hour = `${date.getHours()}`.padStart(2, "0");
  const minute = `${date.getMinutes()}`.padStart(2, "0");
  return `${year}-${month}-${day} ${hour}:${minute}`;
}

function toPercent(value) {
  if (typeof value !== "number") {
    return "-";
  }
  return `${Math.round(value * 100)}%`;
}

function toFullImageUrl(url) {
  if (!url) {
    return "";
  }
  if (
    /^https?:\/\//.test(url) ||
    /^\/static\//.test(url) ||
    /^wxfile:\/\//.test(url) ||
    /^file:\/\//.test(url) ||
    /^data:/.test(url)
  ) {
    return url;
  }
  return `${baseUrl}${url}`;
}

module.exports = {
  formatDateTime,
  toPercent,
  toFullImageUrl
};



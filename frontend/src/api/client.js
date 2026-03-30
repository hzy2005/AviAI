const { request } = require("../../utils/request");

function apiClient(config) {
  return request(config);
}

module.exports = {
  apiClient
};

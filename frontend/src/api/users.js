const { apiClient } = require("./client");

function getCurrentUser() {
  return apiClient({
    url: "/api/v1/users/me"
  });
}

module.exports = {
  getCurrentUser
};

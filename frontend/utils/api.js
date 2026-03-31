const { auth, birds, posts, users } = require("../src/api/index");

module.exports = {
  authApi: auth,
  userApi: users,
  birdApi: birds,
  postApi: posts
};

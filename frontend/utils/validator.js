function isValidEmail(email) {
  const value = String(email || "").trim();
  // RFC-compliant enough for app-side validation while keeping UX simple.
  return /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(value);
}

module.exports = {
  isValidEmail
};

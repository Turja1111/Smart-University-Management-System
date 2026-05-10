const TOKEN_KEYS = {
  access: "access_token",
  refresh: "refresh_token",
};

const USER_KEY = "sums_user";

export function getToken() {
  return localStorage.getItem(TOKEN_KEYS.access);
}

export function getRefreshToken() {
  return localStorage.getItem(TOKEN_KEYS.refresh);
}

export function setTokens({ access, refresh }) {
  if (access) localStorage.setItem(TOKEN_KEYS.access, access);
  if (refresh) localStorage.setItem(TOKEN_KEYS.refresh, refresh);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEYS.access);
  localStorage.removeItem(TOKEN_KEYS.refresh);
}

export function getUser() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getRole() {
  return getUser()?.role || null;
}

export function isLoggedIn() {
  return !!getToken();
}

export function logout() {
  clearTokens();
  localStorage.removeItem(USER_KEY);
  window.location.href = "/login/";
}

export function getInitials() {
  const user = getUser();
  if (!user) return "?";
  const name = `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.email || "User";
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function getDisplayName() {
  const user = getUser();
  if (!user) return "User";
  const full = `${user.first_name || ""} ${user.last_name || ""}`.trim();
  return full || user.email || "User";
}


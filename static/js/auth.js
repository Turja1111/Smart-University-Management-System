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

export function isVerified() {
  return getUser()?.is_verified === true;
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

export function renderNameWithBadge(name, verified) {
  if (!verified) return name;
  return `${name} <svg style="display:inline-block; vertical-align:middle; margin-left:4px; color:#3b82f6;" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>`;
}


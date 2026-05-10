export function debounce(fn, ms) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}

export function formatDate(d) {
  try {
    const dt = typeof d === "string" ? new Date(d) : d;
    return dt.toLocaleDateString();
  } catch {
    return "—";
  }
}

export function countUp(el, target, duration = 1200, decimals = 0, suffix = "") {
  const step = 16;
  const total = Math.max(1, Math.floor(duration / step));
  let i = 0;
  const start = 0;
  const end = Number.isFinite(target) ? target : 0;
  const timer = setInterval(() => {
    i += 1;
    const v = start + (end - start) * (i / total);
    el.textContent = v.toFixed(decimals) + suffix;
    if (i >= total) clearInterval(timer);
  }, step);
}


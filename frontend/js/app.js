// ===== Fait par Mathis Duvivé et Alexandre Pech--Rossell =====
// ===== DÉFI SANTÉ — API CLIENT & UTILITIES =====

const API_BASE = "http://localhost:5000/api";

// ===== AUTH =====
const Auth = {
  getToken: () => localStorage.getItem("ds_token"),
  getUser: () => JSON.parse(localStorage.getItem("ds_user") || "null"),
  setSession: (token, user) => {
    localStorage.setItem("ds_token", token);
    localStorage.setItem("ds_user", JSON.stringify(user));
  },
  clear: () => {
    localStorage.removeItem("ds_token");
    localStorage.removeItem("ds_user");
  },
  isLoggedIn: () => !!localStorage.getItem("ds_token"),
  isGestionnaire: () => {
    const u = Auth.getUser();
    return u && u.role === "gestionnaire";
  },
  requireAuth: () => {
    if (!Auth.isLoggedIn()) {
      window.location.href = "/";
      return false;
    }
    return true;
  },
};

// ===== HTTP CLIENT =====
async function api(method, endpoint, body = null) {
  const headers = { "Content-Type": "application/json" };
  const token = Auth.getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(API_BASE + endpoint, opts);

  if (res.status === 401) {
    Auth.clear();
    window.location.href = "/";
    return;
  }

  // Vérifier que la réponse est bien du JSON avant d'appeler .json()
  // (Flask peut retourner du HTML pour certaines erreurs)
  const contentType = res.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    throw new Error(`Erreur serveur (${res.status}) — réponse inattendue du serveur.`);
  }

  const data = await res.json();
  if (!res.ok) throw new Error(data.erreur || data.message || "Erreur serveur");
  return data;
}

const GET = (ep) => api("GET", ep);
const POST = (ep, body) => api("POST", ep, body);
const PUT = (ep, body) => api("PUT", ep, body);
const DELETE = (ep) => api("DELETE", ep);

// ===== DOM HELPERS =====
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function el(tag, attrs = {}, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v;
    else if (k === "html") e.innerHTML = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v);
  }
  children.forEach(c => {
    if (typeof c === "string") e.insertAdjacentHTML("beforeend", c);
    else if (c) e.appendChild(c);
  });
  return e;
}

function showAlert(container, msg, type = "error") {
  const icons = { success: "✅", error: "❌", info: "ℹ️", warning: "⚠️" };
  const div = document.createElement("div");
  div.className = `alert alert-${type}`;
  div.innerHTML = `<span>${icons[type]}</span><span>${msg}</span>`;
  if (typeof container === "string") container = $(container);
  container.innerHTML = "";
  container.appendChild(div);
  if (type === "success") setTimeout(() => div.remove(), 4000);
}

function showLoading(container) {
  if (typeof container === "string") container = $(container);
  container.innerHTML = '<div class="loading-center"><div class="spinner"></div></div>';
}

function emptyState(icon, title, subtitle = "") {
  let subtitleHTML = "";
  if (subtitle) {
    subtitleHTML = "<p>" + subtitle + "</p>";
  }

  return `<div class="empty-state">
    <div class="empty-state-icon">${icon}</div>
    <div class="empty-state-title">${title}</div>
    ${subtitleHTML}
  </div>`;
}

// ===== NAVIGATION =====
function initNav() {
  const user = Auth.getUser();
  if (!user) return;

  const initials = (user.prenom[0] + user.nom[0]).toUpperCase();
  const nav = document.querySelector(".nav");
  if (!nav) return;

  const userDiv = nav.querySelector(".nav-user");
  if (userDiv) {
    userDiv.innerHTML = `
      <div class="nav-avatar">${initials}</div>
      <span class="nav-user-name">${user.prenom}</span>
      <button class="btn btn-gris btn-sm" onclick="logout()">Déconnexion</button>
    `;
  }

  // Highlight active link
  const currentPage = window.location.pathname.split("/").pop();
  $$(".nav-link").forEach(link => {
    const href = link.getAttribute("href")?.split("/").pop();
    if (href === currentPage) link.classList.add("active");
  });

  // Hide gestionnaire links for participants
  if (!Auth.isGestionnaire()) {
    $$(".nav-gestionnaire").forEach(l => l.remove());
  }
}

function logout() {
  Auth.clear();
  window.location.href = "/";
}

// ===== MODALS =====
function openModal(id) { $(`#${id}`)?.classList.remove("hidden"); }
function closeModal(id) { $(`#${id}`)?.classList.add("hidden"); }

document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-backdrop")) {
    e.target.classList.add("hidden");
  }
  if (e.target.classList.contains("modal-close")) {
    e.target.closest(".modal-backdrop")?.classList.add("hidden");
  }
});

// ===== TABS =====
function initTabs(container = document) {
  $$(".tab-btn", container).forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;
      const group = btn.closest(".tabs")?.dataset.group || "";
      $$(".tab-btn", container).filter(b => (b.closest(".tabs")?.dataset.group || "") === group)
        .forEach(b => b.classList.remove("active"));
      $$(".tab-panel", container).filter(p => p.dataset.group === group)
        .forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      $(`[data-panel="${target}"]`, container)?.classList.add("active");
    });
  });
}

// ===== FORMATTERS =====
const fmt = {
  pts: (n) => `${parseFloat(n).toFixed(1)} pts`,
  mins: (n) => {
    const h = Math.floor(n / 60);
    const m = n % 60;
    return h > 0 ? `${h}h${m > 0 ? m + "m" : ""}` : `${m} min`;
  },
  date: (d) => new Date(d + "T00:00:00").toLocaleDateString("fr-CA", { day: "numeric", month: "short", year: "numeric" }),
  rang: (r) => {
    if (r === 1) return "🥇";
    if (r === 2) return "🥈";
    if (r === 3) return "🥉";
    return `#${r}`;
  },
  sexe: (s) => ({ homme: "Homme", femme: "Femme", mixte: "Mixte" }[s] || s),
  intensite: (i) => ({ faible: "🔵 Faible", moyenne: "🟡 Moyenne", intense: "🔴 Intense" }[i] || i),
};

// ===== INIT =====
document.addEventListener("DOMContentLoaded", () => {
  initNav();
  initTabs();
});

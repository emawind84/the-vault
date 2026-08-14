(function () {
  "use strict";

  var THEME_KEY = "vault-theme";

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", theme === "dark");
    });
  }

  function initTheme() {
    var stored = localStorage.getItem(THEME_KEY);
    if (stored) applyTheme(stored);

    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var current = document.documentElement.getAttribute("data-theme");
        if (!current) {
          current = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }
        var next = current === "dark" ? "light" : "dark";
        localStorage.setItem(THEME_KEY, next);
        applyTheme(next);
      });
    });
  }

  function initSidenav() {
    var sidenav = document.querySelector("[data-sidenav]");
    var backdrop = document.querySelector("[data-sidenav-backdrop]");
    if (!sidenav) return;

    function close() {
      sidenav.classList.remove("is-open");
      if (backdrop) backdrop.classList.remove("is-open");
    }

    function open() {
      sidenav.classList.add("is-open");
      if (backdrop) backdrop.classList.add("is-open");
    }

    document.querySelectorAll("[data-sidenav-toggle]").forEach(function (btn) {
      btn.addEventListener("click", open);
    });
    document.querySelectorAll("[data-sidenav-close]").forEach(function (el) {
      el.addEventListener("click", close);
    });
    if (backdrop) backdrop.addEventListener("click", close);
  }

  function initPasswordToggles() {
    document.querySelectorAll("[data-toggle-password]").forEach(function (btn) {
      var targetId = btn.getAttribute("data-toggle-password");
      var input = document.getElementById(targetId);
      if (!input) return;
      btn.addEventListener("click", function () {
        var showing = input.type === "text";
        input.type = showing ? "password" : "text";
        btn.setAttribute("aria-label", showing ? "Show password" : "Hide password");
        var showEl = btn.querySelector("[data-icon-show]");
        var hideEl = btn.querySelector("[data-icon-hide]");
        if (showEl && hideEl) {
          showEl.style.display = showing ? "" : "none";
          hideEl.style.display = showing ? "none" : "";
        }
      });
    });
  }

  function showToast(message) {
    var toast = document.querySelector("[data-toast]");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(toast._hideTimer);
    toast._hideTimer = window.setTimeout(function () {
      toast.classList.remove("is-visible");
    }, 2200);
  }

  function initClipboard() {
    document.querySelectorAll("[data-copy-target]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var target = document.getElementById(btn.getAttribute("data-copy-target"));
        if (!target) return;
        var text = target.value !== undefined ? target.value : target.textContent;
        navigator.clipboard.writeText(text).then(function () {
          showToast(btn.getAttribute("data-copy-message") || "Copied to clipboard");
        });
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    initSidenav();
    initPasswordToggles();
    initClipboard();
  });
})();

/* HeartPath website behaviour. No tracking, no cookies.
 *
 * To publish a new app version: put the new APK in downloads/ and update
 * APP below (see README.md). Everything on the page reads from here.
 */
(function () {
  "use strict";

  var APP = {
    version: "1.0.0",
    build: 2,
    sizeMB: 71,
    file: "downloads/HeartPath-1.0.0.apk",
    sha256: "dc981ba411aec17b591d5fe8ef76ad26f35983414e6883172c3cd6bba88d8463",
    email: "heartrehab.chathurthasen@gmail.com"
  };

  var LANGS = ["si", "ta", "en"];
  var STORE_KEY = "heartpath-lang";
  var dict = window.HP_I18N || {};
  var root = document.documentElement;
  var page = root.getAttribute("data-page") || "home";

  // ------------------------------------------------------------ language
  function fill(text) {
    return String(text)
      .replace(/\{size\}/g, APP.sizeMB)
      .replace(/\{version\}/g, APP.version)
      .replace(/\{email\}/g, APP.email);
  }

  function t(lang, key) {
    var table = dict[lang] || {};
    var value = table[key] != null ? table[key] : (dict.en || {})[key];
    return value == null ? null : fill(value);
  }

  function savedLang() {
    try { return localStorage.getItem(STORE_KEY); } catch (e) { return null; }
  }

  function pickLang() {
    var fromUrl = new URLSearchParams(location.search).get("lang");
    if (LANGS.indexOf(fromUrl) >= 0) return fromUrl;
    var saved = savedLang();
    if (LANGS.indexOf(saved) >= 0) return saved;
    var prefs = navigator.languages || [navigator.language || ""];
    for (var i = 0; i < prefs.length; i++) {
      var code = String(prefs[i]).toLowerCase().slice(0, 2);
      if (code === "si" || code === "ta") return code;
    }
    return "en";
  }

  function applyLang(lang, remember) {
    root.lang = lang;

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var v = t(lang, el.getAttribute("data-i18n"));
      if (v != null) el.textContent = v;
    });
    // Only our own strings from i18n.js go through innerHTML.
    document.querySelectorAll("[data-i18n-html]").forEach(function (el) {
      var v = t(lang, el.getAttribute("data-i18n-html"));
      if (v != null) el.innerHTML = v;
    });
    document.querySelectorAll("[data-i18n-attr]").forEach(function (el) {
      el.getAttribute("data-i18n-attr").split(";").forEach(function (pair) {
        var parts = pair.split(":");
        var v = t(lang, parts[1]);
        if (v != null) el.setAttribute(parts[0], v);
      });
    });

    var title = t(lang, page === "privacy" ? "pp_meta_title" : "meta_title");
    if (title) document.title = title;
    var desc = document.querySelector('meta[name="description"]');
    var d = t(lang, "meta_desc");
    if (desc && d) desc.setAttribute("content", d);

    document.querySelectorAll(".lang-switch button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-lang") === lang));
    });

    // The hero shows the app in Sinhala when Sinhala is chosen.
    document.querySelectorAll(".js-hero-shot").forEach(function (img) {
      var def = img.getAttribute("data-src-default") || img.getAttribute("src");
      img.setAttribute("data-src-default", def);
      var si = img.getAttribute("data-src-si");
      img.src = lang === "si" && si ? si : def;
    });

    if (remember) {
      try { localStorage.setItem(STORE_KEY, lang); } catch (e) { /* private mode */ }
      var url = new URL(location.href);
      url.searchParams.set("lang", lang);
      history.replaceState(null, "", url);
    }
  }

  document.querySelectorAll(".lang-switch button").forEach(function (b) {
    b.addEventListener("click", function () { applyLang(b.getAttribute("data-lang"), true); });
  });

  // Keep links between pages in the same language.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href$=".html"], a[href="./"], a[href="index.html"]');
    if (!a || root.lang === "en") return;
    var url = new URL(a.getAttribute("href"), location.href);
    url.searchParams.set("lang", root.lang);
    a.setAttribute("href", url.pathname.split("/").pop() + url.search + url.hash);
  });

  // ------------------------------------------------------------ app facts
  document.querySelectorAll(".js-download").forEach(function (a) { a.setAttribute("href", APP.file); });
  document.querySelectorAll(".js-version").forEach(function (el) { el.textContent = APP.version + " (" + APP.build + ")"; });
  document.querySelectorAll(".js-size").forEach(function (el) { el.textContent = APP.sizeMB; });
  document.querySelectorAll(".js-sha").forEach(function (el) { el.textContent = APP.sha256; });
  document.querySelectorAll(".js-year").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  // ------------------------------------------------------------ device
  var ua = navigator.userAgent || "";
  var isIOS = /iPhone|iPad|iPod/i.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  var isAndroid = /Android/i.test(ua);
  var device = isIOS ? "ios" : isAndroid ? "android" : (matchMedia("(pointer: coarse)").matches ? "android" : "desktop");
  root.setAttribute("data-device", device);

  // On a computer, show a QR code so the page can be opened on the phone.
  function drawQr() {
    var box = document.getElementById("qr");
    if (!box || typeof window.qrcode !== "function") return;
    var url = new URL(location.href);
    url.hash = "";
    var qr = window.qrcode(0, "M");
    qr.addData(url.toString());
    qr.make();
    box.innerHTML = qr.createSvgTag({ cellSize: 4, margin: 1, scalable: true });
    var svg = box.querySelector("svg");
    if (svg) {
      svg.querySelectorAll("rect").forEach(function (r) { r.setAttribute("fill", "#fff"); });
      svg.querySelectorAll("path").forEach(function (p) { p.setAttribute("fill", "#063f3c"); });
    }
  }
  if (device === "desktop" && page === "home" && location.protocol !== "file:") {
    var s = document.createElement("script");
    s.src = "https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js";
    s.async = true;
    s.onload = drawQr;
    document.head.appendChild(s);
  }

  // ------------------------------------------------------------ download help
  var toast = document.querySelector(".toast");
  var toastTimer;
  function showToast(text) {
    if (!toast) return;
    toast.textContent = text;
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove("is-visible"); }, 6000);
  }

  document.querySelectorAll(".js-download").forEach(function (a) {
    a.addEventListener("click", function () {
      if (device === "ios") return;
      showToast(t(root.lang, "toast_started"));
      // Bring the next step into view while the file downloads.
      var step = document.getElementById("step-2");
      if (!step) return;
      setTimeout(function () {
        step.scrollIntoView({ behavior: "smooth", block: "center" });
        step.classList.add("is-highlight");
        setTimeout(function () { step.classList.remove("is-highlight"); }, 4000);
      }, 900);
    });
  });

  // ------------------------------------------------------------ sticky bar
  var bar = document.querySelector(".sticky-dl");
  var watched = [document.getElementById("hero-cta"), document.getElementById("final-cta")].filter(Boolean);
  if (bar && watched.length && "IntersectionObserver" in window) {
    var visible = new Set();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) visible.add(en.target); else visible.delete(en.target);
      });
      var show = visible.size === 0 && window.scrollY > 200;
      bar.classList.toggle("is-visible", show);
      bar.setAttribute("aria-hidden", String(!show));
      var link = bar.querySelector("a");
      if (link) link.tabIndex = show ? 0 : -1;
    });
    watched.forEach(function (el) { io.observe(el); });
  }

  // ------------------------------------------------------------ gallery arrows (desktop)
  var gallery = document.querySelector(".gallery");
  function slide(dir) {
    if (!gallery) return;
    var card = gallery.querySelector("figure");
    var step = card ? card.getBoundingClientRect().width + 18 : 260;
    gallery.scrollBy({ left: dir * step * 2, behavior: "smooth" });
  }
  var prev = document.querySelector(".js-gal-prev");
  var next = document.querySelector(".js-gal-next");
  if (prev) prev.addEventListener("click", function () { slide(-1); });
  if (next) next.addEventListener("click", function () { slide(1); });

  // ------------------------------------------------------------ start
  applyLang(pickLang(), false);
})();

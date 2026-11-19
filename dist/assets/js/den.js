/* THE DEN — site interactions. Vanilla, no dependencies, ~4 KB. */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.remove("no-js");

  /* Header: solid state after scrolling */
  var header = document.querySelector(".site-header");
  var mcta = document.querySelector(".m-cta");
  var ticking = false;
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle("is-scrolled", y > 24);
    if (mcta) mcta.classList.toggle("is-visible", y > window.innerHeight * 0.8);
    ticking = false;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { window.requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });
  onScroll();

  /* Desktop dropdowns: click/keyboard support in addition to hover */
  document.querySelectorAll(".nav__item.has-dropdown").forEach(function (item) {
    var btn = item.querySelector(".nav__link");
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      var open = !item.classList.contains("is-open");
      document.querySelectorAll(".nav__item.is-open").forEach(function (o) {
        o.classList.remove("is-open");
        o.querySelector(".nav__link").setAttribute("aria-expanded", "false");
      });
      item.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", String(open));
    });
    item.addEventListener("mouseleave", function () {
      item.classList.remove("is-open");
      btn.setAttribute("aria-expanded", "false");
    });
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".nav__item")) {
      document.querySelectorAll(".nav__item.is-open").forEach(function (o) {
        o.classList.remove("is-open");
        o.querySelector(".nav__link").setAttribute("aria-expanded", "false");
      });
    }
  });

  /* Mobile drawer */
  var drawer = document.getElementById("drawer");
  var toggle = document.querySelector(".nav-toggle");
  var lastFocus = null;
  function setDrawer(open) {
    if (!drawer) return;
    drawer.classList.toggle("is-open", open);
    drawer.setAttribute("aria-hidden", String(!open));
    document.body.classList.toggle("drawer-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", String(open));
    if (open) {
      lastFocus = document.activeElement;
      var first = drawer.querySelector("button, a");
      if (first) first.focus();
    } else if (lastFocus) {
      lastFocus.focus();
    }
  }
  if (toggle) toggle.addEventListener("click", function () { setDrawer(true); });
  if (drawer) {
    drawer.querySelectorAll("[data-close]").forEach(function (el) {
      el.addEventListener("click", function () { setDrawer(false); });
    });
    drawer.querySelectorAll(".m-nav button").forEach(function (b) {
      b.addEventListener("click", function () {
        var list = document.getElementById(b.getAttribute("aria-controls"));
        var open = b.getAttribute("aria-expanded") !== "true";
        b.setAttribute("aria-expanded", String(open));
        if (list) list.classList.toggle("is-open", open);
      });
    });
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      setDrawer(false);
      document.querySelectorAll(".nav__item.is-open").forEach(function (o) { o.classList.remove("is-open"); });
    }
  });

  /* Reveal on scroll */
  var els = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    doc.classList.add("js-reveal");
    var vh = window.innerHeight;
    els.forEach(function (el) { if (el.getBoundingClientRect().top < vh) el.classList.add("is-in"); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* Hero: dealt cards follow the pointer slightly */
  var deal = document.querySelector("[data-tilt]");
  if (deal && window.matchMedia("(hover: hover) and (prefers-reduced-motion: no-preference)").matches) {
    var hero = deal.closest("section") || deal;
    hero.addEventListener("mousemove", function (e) {
      var r = hero.getBoundingClientRect();
      deal.style.setProperty("--mx", ((e.clientX - r.left) / r.width - 0.5).toFixed(3) * 2);
      deal.style.setProperty("--my", ((e.clientY - r.top) / r.height - 0.5).toFixed(3) * 2);
    });
    hero.addEventListener("mouseleave", function () { deal.style.setProperty("--mx", 0); deal.style.setProperty("--my", 0); });
  }

  /* Intro panels: tap / keyboard opens a panel */
  document.querySelectorAll(".h-panel").forEach(function (p) {
    function open() {
      document.querySelectorAll(".h-panel.is-open").forEach(function (o) { o.classList.remove("is-open"); });
      p.classList.add("is-open");
    }
    p.addEventListener("click", open);
    p.addEventListener("focus", open);
  });

  /* Elementor Pro form endpoint (same fields, IDs and handler as the live site).
     Works when served from pokerattheden.com; elsewhere it falls back to phone/email. */
  document.querySelectorAll("form[data-elementor-form]").forEach(function (form) {
    var status = form.querySelector(".form-status");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      if (window.DEN_PREVIEW) {
        status.textContent = "Design preview: this form isn\u2019t connected here. On the live site it sends your message to The Den.";
        status.className = "form-status is-ok";
        return;
      }
      var btn = form.querySelector("[type=submit]");
      var label = btn.textContent;
      btn.disabled = true; btn.textContent = "Sending…";
      status.className = "form-status";
      var data = new FormData(form);
      data.append("action", "elementor_pro_forms_send_form");
      data.append("referrer", window.location.href);
      fetch("/wp-admin/admin-ajax.php", { method: "POST", body: data, credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res && res.success) {
            status.textContent = (res.data && res.data.message) || "Thank you — your message has been sent.";
            status.className = "form-status is-ok";
            form.reset();
          } else { throw new Error("rejected"); }
        })
        .catch(function () {
          status.innerHTML = 'We couldn’t send your message just now. Please call <a href="tel:+12145014909">+1 (214) 501-4909</a> or email <a href="mailto:jamiekempf@ymail.com">jamiekempf@ymail.com</a>.';
          status.className = "form-status is-err";
        })
        .then(function () { btn.disabled = false; btn.textContent = label; });
    });
  });
})();

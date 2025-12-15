(() => {
  const restoreSidebarScroll = () => {
    const sidebar = document.querySelector(".learning-sidebar");
    if (!sidebar) return;
    try {
      const raw = sessionStorage.getItem("techdocs_sidebar_scroll");
      const y = raw != null ? Number(raw) : null;
      if (y != null && Number.isFinite(y)) sidebar.scrollTop = y;
    } catch (e) {}
  };

  const wireSidebarScrollPersistence = () => {
    const sidebar = document.querySelector(".learning-sidebar");
    if (!sidebar) return;
    let raf = 0;
    const save = () => {
      raf = 0;
      try {
        sessionStorage.setItem("techdocs_sidebar_scroll", String(sidebar.scrollTop || 0));
      } catch (e) {}
    };
    sidebar.addEventListener("scroll", () => {
      if (raf) return;
      raf = window.requestAnimationFrame(save);
    });
    window.addEventListener("beforeunload", save);
  };

  const buildOutline = () => {
    const host = document.getElementById("techdocs-outline");
    const root = document.querySelector(".learning-md");
    if (!host || !root) return;
    host.innerHTML = "";

    const headings = Array.from(root.querySelectorAll("h2, h3"));
    headings.forEach((h, idx) => {
      if (!h.id) h.id = `sec-${idx + 1}`;
      const level = h.tagName === "H2" ? "level-1" : "level-2";
      const a = document.createElement("a");
      a.className = `outline-item ${level}`;
      a.href = `#${h.id}`;
      a.textContent = h.textContent || "";
      host.appendChild(a);
    });

    if (!headings.length) {
      const empty = document.createElement("div");
      empty.className = "muted";
      empty.textContent = "（本页没有标题层级）";
      empty.style.fontSize = "13px";
      host.appendChild(empty);
      return;
    }

    const itemsById = new Map();
    Array.from(host.querySelectorAll("a.outline-item")).forEach((a) => {
      const id = String(a.getAttribute("href") || "").replace(/^#/, "");
      if (id) itemsById.set(id, a);
    });

    const setActive = (id) => {
      itemsById.forEach((el, key) => {
        if (key === id) el.classList.add("active");
        else el.classList.remove("active");
      });
    };

    try {
      const observer = new IntersectionObserver(
        (entries) => {
          const visible = entries
            .filter((e) => e.isIntersecting)
            .sort((a, b) => (a.boundingClientRect.top || 0) - (b.boundingClientRect.top || 0));
          if (visible.length) {
            const id = visible[0]?.target?.id;
            if (id) setActive(id);
          }
        },
        { root: null, rootMargin: "-20% 0px -70% 0px", threshold: [0, 1] }
      );
      headings.forEach((h) => observer.observe(h));
      setActive(headings[0]?.id);
    } catch (e) {
      // ignore
    }
  };

  const openToc = () => {
    const overlay = document.getElementById("techdocs-toc-overlay");
    if (!overlay) return;
    overlay.classList.add("open");
    overlay.setAttribute("aria-hidden", "false");
    document.getElementById("techdocs-toc-filter")?.focus();
  };

  const closeToc = () => {
    const overlay = document.getElementById("techdocs-toc-overlay");
    if (!overlay) return;
    overlay.classList.remove("open");
    overlay.setAttribute("aria-hidden", "true");
  };

  const filterToc = () => {
    const input = document.getElementById("techdocs-toc-filter");
    const list = document.getElementById("techdocs-toc-list");
    if (!input || !list) return;
    const q = (input.value || "").trim().toLowerCase();
    Array.from(list.querySelectorAll("a.toc-item")).forEach((a) => {
      const slug = String(a.getAttribute("data-slug") || "").toLowerCase();
      const title = String(a.getAttribute("data-title") || "").toLowerCase();
      const hit = !q || slug.includes(q) || title.includes(q);
      a.style.display = hit ? "" : "none";
    });
  };

  restoreSidebarScroll();
  wireSidebarScrollPersistence();
  buildOutline();

  document.getElementById("techdocs-toc-open")?.addEventListener("click", openToc);
  document.getElementById("techdocs-toc-close")?.addEventListener("click", closeToc);
  document.getElementById("techdocs-toc-overlay")?.addEventListener("click", (e) => {
    if (e.target?.id === "techdocs-toc-overlay") closeToc();
  });
  document.getElementById("techdocs-toc-filter")?.addEventListener("input", filterToc);
})();


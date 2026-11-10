document.addEventListener("DOMContentLoaded", () => {
  const year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  const toggle = document.querySelector(".nav-toggle");
  const menu = document.getElementById("site-menu");
  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const isOpen = menu.getAttribute("data-open") === "true";
      menu.setAttribute("data-open", String(!isOpen));
      toggle.setAttribute("aria-expanded", String(!isOpen));
    });
  }

  // Mark current page in nav
  const links = document.querySelectorAll(".menu a");
  links.forEach((link) => {
    if (link.getAttribute("href") === location.pathname.split("/").pop()) {
      link.setAttribute("aria-current", "page");
    }
  });

  // (removed trifecta interactions)

  // Members filtering
  const membersContainer = document.getElementById("members");
  const labsChips = document.getElementById("chips-labs");
  const rolesChips = document.getElementById("chips-roles");
  const searchInput = document.getElementById("filter-search");
  const filterControls = [labsChips, rolesChips, searchInput];

  function normalise(text) {
    return (text || "").toString().toLowerCase().trim();
  }

  function applyFilters() {
    if (!membersContainer) return;
    // Collect selected labs/roles from chips (multi-select)
    const selectedLabs = labsChips
      ? Array.from(labsChips.querySelectorAll('.chip[aria-pressed="true"]')).map((b) => b.getAttribute('data-value'))
      : [];
    const selectedRoles = rolesChips
      ? Array.from(rolesChips.querySelectorAll('.chip[aria-pressed="true"]')).map((b) => b.getAttribute('data-value'))
      : [];
    const query = normalise(searchInput ? searchInput.value : "");

    const cards = membersContainer.querySelectorAll(".member");
    cards.forEach((card) => {
      // Support multiple labs/roles via comma-separated lists
      const labsAttr = card.getAttribute("data-labs") || card.getAttribute("data-lab") || "";
      const rolesAttr = card.getAttribute("data-roles") || card.getAttribute("data-role") || "";
      const cardLabs = labsAttr.split(",").map((s) => s.trim()).filter(Boolean);
      const cardRoles = rolesAttr.split(",").map((s) => s.trim()).filter(Boolean);
      const name = normalise(card.querySelector("h3")?.textContent);
      const details = normalise(card.querySelector("p")?.textContent);
      const keywords = normalise(card.getAttribute("data-keywords"));

      const labMatch = selectedLabs.length === 0 || selectedLabs.some((v) => cardLabs.includes(v));
      const roleMatch = selectedRoles.length === 0 || selectedRoles.some((v) => cardRoles.includes(v));
      const text = `${name} ${details} ${keywords}`;
      const searchMatch = !query || text.includes(query);

      const isVisible = labMatch && roleMatch && searchMatch;
      card.style.display = isVisible ? "block" : "none";
    });
  }

  // Wire up chip toggles
  function wireChips(container) {
    if (!container) return;
    container.addEventListener("click", (e) => {
      const target = e.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("chip")) return;
      const pressed = target.getAttribute("aria-pressed") === "true";
      target.setAttribute("aria-pressed", String(!pressed));
      applyFilters();
    });
  }

  wireChips(labsChips);
  wireChips(rolesChips);
  if (searchInput) searchInput.addEventListener("input", applyFilters);

  applyFilters();

  // Member card expansion: only one expands on hover/focus/click
  if (membersContainer) {
    const cards = Array.from(membersContainer.querySelectorAll('.member'));

    function collapseAll(except) {
      cards.forEach((c) => {
        if (c !== except) c.classList.remove('expanded');
      });
    }

    function expand(card) {
      collapseAll(card);
      card.classList.add('expanded');
    }

    function collapse(card) {
      card.classList.remove('expanded');
    }

    cards.forEach((card) => {
      card.addEventListener('mouseenter', () => expand(card));
      card.addEventListener('mouseleave', () => collapse(card));

      card.addEventListener('focusin', () => expand(card));
      card.addEventListener('focusout', () => {
        // Delay to allow focus to move within the same card
        setTimeout(() => {
          if (!card.contains(document.activeElement)) {
            collapse(card);
          }
        }, 0);
      });

      // Click/touch toggle for mobile (ignore clicks on links inside details)
      card.addEventListener('click', (e) => {
        if (e.target instanceof Element && e.target.closest('a')) return;
        const isExpanded = card.classList.contains('expanded');
        if (isExpanded) {
          collapse(card);
        } else {
          expand(card);
        }
        e.stopPropagation();
      });
    });

    // Click outside to collapse
    document.addEventListener('click', (e) => {
      const target = e.target;
      if (!(target instanceof Node)) return;
      if (!membersContainer.contains(target)) {
        collapseAll(undefined);
      }
    });
  }

  // Prefetch internal HTML pages on hover/touchstart for near-instant navigation
  const prefetched = new Set();
  function prefetchPage(href) {
    if (!href || href.startsWith("#") || href.startsWith("mailto:") || href.includes("://")) return;
    const page = href.split("#")[0];
    if (!page.endsWith(".html") || prefetched.has(page)) return;
    prefetched.add(page);
    const link = document.createElement("link");
    link.rel = "prefetch";
    link.href = page;
    document.head.appendChild(link);
  }

  document.addEventListener("mouseover", (e) => {
    const a = e.target instanceof Element ? e.target.closest("a[href]") : null;
    if (a) prefetchPage(a.getAttribute("href"));
  }, { passive: true });

  document.addEventListener("touchstart", (e) => {
    const a = e.target instanceof Element ? e.target.closest("a[href]") : null;
    if (a) prefetchPage(a.getAttribute("href"));
  }, { passive: true });
});



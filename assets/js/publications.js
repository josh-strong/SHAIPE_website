document.addEventListener("DOMContentLoaded", () => {
  // Copy-citation buttons on publication detail pages
  document.querySelectorAll("[data-copy-citation]").forEach((button) => {
    const citation = document.getElementById(button.dataset.copyCitation);
    const status = document.getElementById(button.getAttribute("aria-describedby"));
    if (!citation || !status) return;

    button.hidden = false;
    button.addEventListener("click", async () => {
      const text = citation.textContent.replace(/\s+/g, " ").trim();
      try {
        if (!navigator.clipboard || !window.isSecureContext) {
          throw new Error("Clipboard unavailable");
        }
        await navigator.clipboard.writeText(text);
        status.textContent = "Citation copied.";
      } catch {
        const selection = window.getSelection();
        if (!selection) {
          status.textContent = "Select the citation above and copy it.";
          return;
        }
        const range = document.createRange();
        range.selectNodeContents(citation);
        selection.removeAllRanges();
        selection.addRange(range);
        status.textContent = "Citation selected. Press Ctrl+C (or ⌘C) to copy.";
      }
    });
  });

  // Populate publication & citation metrics from assets/data/metrics.json
  const metricTargets = document.querySelectorAll("[data-metric]");
  const citationTargets = document.querySelectorAll("[data-citation-doi]");
  if (metricTargets.length || citationTargets.length) {
    fetch("assets/data/metrics.json")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!data || !data.totals) return;

        const { publications = 0, citations = 0, open_access } = data.totals;
        const oaCount = typeof open_access === "number" ? open_access : publications;
        const oaPercent = publications > 0 ? `${Math.round((oaCount / publications) * 100)}%` : "100%";

        const summaryValues = {
          "total-publications": String(publications),
          "total-citations": String(citations),
          "open-access": oaPercent,
        };

        metricTargets.forEach((el) => {
          const key = el.dataset.metric;
          if (key && Object.prototype.hasOwnProperty.call(summaryValues, key)) {
            el.textContent = summaryValues[key];
          }
        });

        if (Array.isArray(data.publications) && citationTargets.length) {
          const byDoi = new Map(
            data.publications
              .filter((item) => item && typeof item.doi === "string")
              .map((item) => [item.doi.toLowerCase(), Number(item.citations) || 0])
          );

          citationTargets.forEach((el) => {
            const doi = (el.dataset.citationDoi || "").toLowerCase();
            if (!byDoi.has(doi)) return;
            const count = byDoi.get(doi);
            if (count > 0) {
              el.textContent = count === 1 ? "1 citation" : `${count} citations`;
              el.hidden = false;
            } else {
              el.textContent = "";
              el.hidden = true;
            }
          });
        }
      })
      .catch(() => {
        // Static HTML fallback values remain visible if offline or file:// preview
      });
  }
});

document.addEventListener("DOMContentLoaded", () => {
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
});

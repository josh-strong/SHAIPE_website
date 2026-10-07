// Obfuscation deters basic address harvesting; it is not encryption.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-email]").forEach((button) => {
    button.hidden = false;
    button.addEventListener("click", () => {
      const bytes = button.dataset.email.match(/.{2}/g).map((byte) => parseInt(byte, 16));
      const key = bytes.shift();
      const address = bytes.map((byte) => String.fromCharCode(byte ^ key)).join("");
      const link = document.createElement("a");
      link.href = "mailto:" + address;
      link.textContent = address;
      button.replaceWith(link);
      link.focus();
    }, { once: true });
  });
});

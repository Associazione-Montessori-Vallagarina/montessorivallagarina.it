document.addEventListener("click", async (event) => {
  const button = event.target.closest(".event-share");
  if (!button) return;

  const url = new URL(button.dataset.shareUrl || window.location.href, document.baseURI);
  url.hash = "";
  try {
    await navigator.clipboard.writeText(url.href);
    const label = button.querySelector(".event-share-label");
    label.textContent = "Link copiato!";
    window.setTimeout(() => { label.textContent = "Copia il link"; }, 2500);
  } catch {
    window.prompt("Copia il link all'evento:", url.href);
  }
});

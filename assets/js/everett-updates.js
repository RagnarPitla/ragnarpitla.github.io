(() => {
  const normalize = (value) =>
    String(value || "")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");

  const cards = Array.from(document.querySelectorAll("[data-update-card]"));
  const buttons = Array.from(document.querySelectorAll("[data-tag-filter]"));
  const empty = document.querySelector("[data-filter-empty]");
  const live = document.querySelector("[data-filter-live]");

  if (!cards.length || !buttons.length || !empty || !live) return;

  const applyFilter = (requested, announce) => {
    const tag = normalize(requested);
    let shown = 0;

    cards.forEach((card) => {
      const tags = String(card.dataset.tags || "").split("|").map(normalize).filter(Boolean);
      const visible = !tag || tags.includes(tag);
      card.hidden = !visible;
      if (visible) shown += 1;
    });

    buttons.forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        normalize(button.dataset.tagFilter) === tag ? "true" : "false"
      );
    });

    empty.hidden = shown !== 0;
    empty.textContent = shown === 0 ? `No updates tagged ${tag}` : "";
    if (announce) {
      live.textContent = tag
        ? `${shown} update${shown === 1 ? "" : "s"} tagged ${tag}`
        : `Showing all ${shown} updates`;
    }
  };

  const initial = new URLSearchParams(window.location.search).get("tag");
  applyFilter(initial, false);

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const tag = normalize(button.dataset.tagFilter);
      applyFilter(tag, true);
    });
  });
})();

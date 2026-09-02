(() => {
  const rows = document.getElementById("rows");
  const q = document.getElementById("filter-q");
  const type = document.getElementById("filter-type");
  const lang = document.getElementById("filter-lang");
  const diff = document.getElementById("filter-diff");

  /** @type {any[]} */
  let challenges = [];

  // Optional base URL for release assets, e.g. https://github.com/USER/REPO/releases/download
  const RELEASE_BASE = (window.PTK_RELEASE_BASE || "").replace(/\/$/, "");

  function downloadHref(ch) {
    if (!RELEASE_BASE) return null;
    return `${RELEASE_BASE}/${ch.id}/${ch.download}`;
  }

  function render() {
    const query = (q.value || "").trim().toLowerCase();
    const filtered = challenges.filter((ch) => {
      if (type.value && ch.type !== type.value) return false;
      if (lang.value && ch.language !== lang.value) return false;
      if (diff.value && String(ch.difficulty) !== diff.value) return false;
      if (!query) return true;
      const hay = `${ch.name} ${ch.summary} ${(ch.tags || []).join(" ")}`.toLowerCase();
      return hay.includes(query);
    });

    if (!filtered.length) {
      rows.innerHTML = `<tr><td colspan="6">No challenges match.</td></tr>`;
      return;
    }

    rows.innerHTML = filtered
      .map((ch) => {
        const href = downloadHref(ch);
        const btn = href
          ? `<a class="btn" href="${href}">Download</a>`
          : `<a class="btn disabled" title="Set window.PTK_RELEASE_BASE or use GitHub Releases">Download</a>`;
        return `<tr>
          <td data-label="Name"><strong>${escapeHtml(ch.name)}</strong><div style="color:#9aa7b8;font-size:0.85rem">${escapeHtml(ch.summary || "")}</div></td>
          <td data-label="Type"><span class="badge type-${escapeHtml(ch.type)}">${escapeHtml(ch.type)}</span></td>
          <td data-label="Lang">${escapeHtml(ch.language)}</td>
          <td data-label="Diff">${escapeHtml(String(ch.difficulty))}</td>
          <td data-label="Created">${escapeHtml(ch.created || "")}</td>
          <td data-label="">${btn}</td>
        </tr>`;
      })
      .join("");
  }

  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  fetch("./catalog.json")
    .then((r) => {
      if (!r.ok) throw new Error(`catalog.json HTTP ${r.status}`);
      return r.json();
    })
    .then((data) => {
      challenges = data.challenges || [];
      render();
    })
    .catch((err) => {
      rows.innerHTML = `<tr><td colspan="6">Failed to load catalog: ${escapeHtml(err.message)}</td></tr>`;
    });

  [q, type, lang, diff].forEach((el) => el.addEventListener("input", render));
})();

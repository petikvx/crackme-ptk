(() => {
  const rows = document.getElementById("rows");
  const q = document.getElementById("filter-q");
  const type = document.getElementById("filter-type");
  const os = document.getElementById("filter-os");
  const pe = document.getElementById("filter-pe");
  const lang = document.getElementById("filter-lang");
  const diff = document.getElementById("filter-diff");

  /** @type {any[]} */
  let challenges = [];

  const RELEASE_BASE = (window.PTK_RELEASE_BASE || "").replace(/\/$/, "");

  function challengeOs(ch) {
    if (ch.os) return ch.os;
    const arch = ch.arch || "";
    if (arch.startsWith("windows")) return "windows";
    if (arch.startsWith("linux")) return "linux";
    return "unknown";
  }

  function challengePe(ch) {
    if (ch.pe_format) return ch.pe_format;
    const arch = ch.arch || "";
    if (arch === "windows-x86_64") return "PE32+";
    if (arch === "windows-x86") return "PE32";
    return "";
  }

  function downloadHref(ch) {
    if (!RELEASE_BASE) return null;
    return `${RELEASE_BASE}/${ch.id}/${ch.download}`;
  }

  function render() {
    const query = (q.value || "").trim().toLowerCase();
    const filtered = challenges.filter((ch) => {
      if (type.value && ch.type !== type.value) return false;
      if (os.value && challengeOs(ch) !== os.value) return false;
      if (pe.value && challengePe(ch) !== pe.value) return false;
      if (lang.value && ch.language !== lang.value) return false;
      if (diff.value && String(ch.difficulty) !== diff.value) return false;
      if (!query) return true;
      const hay = `${ch.name} ${ch.summary} ${(ch.tags || []).join(" ")} ${challengeOs(ch)} ${challengePe(ch)}`.toLowerCase();
      return hay.includes(query);
    });

    if (!filtered.length) {
      rows.innerHTML = `<tr><td colspan="8">No challenges match.</td></tr>`;
      return;
    }

    rows.innerHTML = filtered
      .map((ch) => {
        const href = downloadHref(ch);
        const btn = href
          ? `<a class="btn" href="${href}">Download</a>`
          : `<a class="btn disabled" title="Set window.PTK_RELEASE_BASE or use GitHub Releases">Download</a>`;
        const osName = challengeOs(ch);
        const peName = challengePe(ch) || "—";
        const peClass = peName === "PE32+" ? "pe32plus" : peName === "PE32" ? "pe32" : "pe-none";
        return `<tr>
          <td data-label="Name"><strong>${escapeHtml(ch.name)}</strong><div style="color:#9aa7b8;font-size:0.85rem">${escapeHtml(ch.summary || "")}</div></td>
          <td data-label="Type"><span class="badge type-${escapeHtml(ch.type)}">${escapeHtml(ch.type)}</span></td>
          <td data-label="OS"><span class="badge os-${escapeHtml(osName)}">${escapeHtml(osName)}</span></td>
          <td data-label="PE"><span class="badge ${peClass}">${escapeHtml(peName)}</span></td>
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
      rows.innerHTML = `<tr><td colspan="8">Failed to load catalog: ${escapeHtml(err.message)}</td></tr>`;
    });

  [q, type, os, pe, lang, diff].forEach((el) => el.addEventListener("input", render));
})();

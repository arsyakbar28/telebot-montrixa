/* Formatting and display helpers */

function formatRp(num) {
  return "Rp " + fmt.format(Number(num || 0));
}

function formatDate(str) {
  if (!str) return "";
  const s = String(str).slice(0, 10);
  if (!s) return "";
  const [y, m, d] = s.split("-");
  return `${d}/${m}/${y}`;
}

function formatDetailDateTime(tx) {
  if (!tx) return "-";
  const months = [
    "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
    "Jul", "Agu", "Sep", "Okt", "Nov", "Des",
  ];
  const baseDate = String(tx.transaction_date || "").slice(0, 10);
  if (!baseDate) return "-";
  const parts = baseDate.split("-");
  if (parts.length !== 3) return "-";
  const y = Number(parts[0]);
  const m = Number(parts[1]);
  const d = Number(parts[2]);
  if (!y || !m || !d || m < 1 || m > 12) return "-";

  let timeText = "";
  const timeSource = tx.created_at || tx.updated_at || "";
  if (timeSource) {
    const dt = new Date(timeSource);
    if (!Number.isNaN(dt.getTime())) {
      const hh = String(dt.getHours()).padStart(2, "0");
      const mm = String(dt.getMinutes()).padStart(2, "0");
      timeText = `${hh}.${mm}`;
    } else {
      const match = String(timeSource).match(/(\d{2}):(\d{2})/);
      if (match) timeText = `${match[1]}.${match[2]}`;
    }
  }

  const dayText = String(d).padStart(2, "0");
  const dateText = `${dayText} ${months[m - 1]} ${y}`;
  return timeText ? `${dateText} ・ ${timeText}` : dateText;
}

function formatPct(n) {
  return fmt.format(Number(n || 0)) + "%";
}

function formatLocalDateISO(d) {
  if (!(d instanceof Date)) return "";
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function getAmountDigits(value) {
  return String(value || "").replace(/\D/g, "");
}

function formatAmountInput(value) {
  const digits = getAmountDigits(value);
  if (!digits) return "";
  return digits.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

function getCategoryKind(icon, name, txType) {
  const text = `${icon || ""} ${name || ""}`.toLowerCase();
  if (/(makan|food|drink|kuliner|resto|warung)/.test(text)) return "food";
  if (/(langgan|subscription|internet|domain|hosting|vps)/.test(text)) return "subscription";
  if (/(transport|bensin|bbm|ojek|tol|parkir)/.test(text)) return "transport";
  if (/(hibur|entertain|game|film|music)/.test(text)) return "entertainment";
  if (/(belanja|shopping|market|store)/.test(text)) return "shopping";
  if (/(gaji|salary|payroll|bonus)/.test(text)) return "salary";
  if (/(kesehatan|health|medis|obat)/.test(text)) return "health";
  if (/(edukasi|education|kursus|sekolah)/.test(text)) return "education";
  if (/(tagihan|bill|listrik|air|pln)/.test(text)) return "bill";
  if (/(kado|gift|donasi|charity)/.test(text)) return "gift";
  if (/(invest|saham|crypto|reksa)/.test(text)) return "investment";
  if (txType === "income") return "income";
  return "default";
}

function getCategorySvg(kind) {
  const map = {
    food: `<svg viewBox="0 0 24 24" fill="none"><path d="M6 3v8M10 3v8M8 3v18M15 3v7a3 3 0 0 0 3 3h0v8" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    subscription: `<svg viewBox="0 0 24 24" fill="none"><path d="M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L2 12V2h10l8.6 8.6a2 2 0 0 1 0 2.8Z" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 7h.01" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>`,
    transport: `<svg viewBox="0 0 24 24" fill="none"><path d="M5 16h14M7 16l1-5h8l1 5M8 16v2M16 16v2M9 11V7h6v4" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    entertainment: `<svg viewBox="0 0 24 24" fill="none"><path d="M15 8h.01M9 8h.01M8 13c1 .8 2.4 1.2 4 1.2s3-.4 4-1.2M7 3h10a4 4 0 0 1 4 4v10a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V7a4 4 0 0 1 4-4Z" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    shopping: `<svg viewBox="0 0 24 24" fill="none"><path d="M6 7h12l-1 12H7L6 7Z" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 7a3 3 0 1 1 6 0" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/></svg>`,
    salary: `<svg viewBox="0 0 24 24" fill="none"><path d="M3 7h18v10H3V7Z" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 10v4M10.5 12H13.5" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/></svg>`,
    health: `<svg viewBox="0 0 24 24" fill="none"><path d="M12 21s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.6-7 10-7 10Z" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    education: `<svg viewBox="0 0 24 24" fill="none"><path d="m3 8 9-5 9 5-9 5-9-5Z" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 10.5V15c0 1.7 2.2 3 5 3s5-1.3 5-3v-4.5" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    bill: `<svg viewBox="0 0 24 24" fill="none"><path d="M7 3h10v18l-2-1.5L13 21l-2-1.5L9 21l-2-1.5L5 21V5a2 2 0 0 1 2-2Z" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 8h6M9 12h6" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/></svg>`,
    gift: `<svg viewBox="0 0 24 24" fill="none"><path d="M20 8H4v13h16V8Z" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 8v13M4 12h16M12 8H8.8a1.8 1.8 0 1 1 0-3.6c2 0 3.2 3.6 3.2 3.6ZM12 8h3.2a1.8 1.8 0 1 0 0-3.6C13.2 4.4 12 8 12 8Z" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    investment: `<svg viewBox="0 0 24 24" fill="none"><path d="M4 19h16M7 15v-3M12 15V8M17 15V5" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    income: `<svg viewBox="0 0 24 24" fill="none"><path d="M12 19V5M6 11l6-6 6 6" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    default: `<svg viewBox="0 0 24 24" fill="none"><path d="M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L2 12V2h10l8.6 8.6a2 2 0 0 1 0 2.8Z" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 7h.01" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>`,
  };
  return map[kind] || map.default;
}

function renderCategoryLabel(icon, name, txType) {
  const categoryName = String(name || "").trim();
  if (!categoryName) return `<span class="cat-fallback">-</span>`;
  const kind = getCategoryKind(icon, categoryName, txType);
  return `
    <span class="cat-inline">
      <span class="cat-icon cat-icon-${kind}" aria-hidden="true">${getCategorySvg(kind)}</span>
      <span class="cat-name">${escapeHtml(categoryName)}</span>
    </span>
  `;
}

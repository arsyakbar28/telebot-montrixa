/* Render transaction list items */

function renderTxItem(t) {
  const sign = t.type === "income" ? "+" : "−";
  const amount = sign + formatRp(Math.abs(Number(t.amount || 0)));
  const cls = t.type === "income" ? "income" : "expense";
  const cat = renderCategoryLabel(t.category_icon, t.category_name, t.type);
  const dateStr = t.transaction_date ? String(t.transaction_date).slice(0, 10) : "";
  const desc = escapeHtml((t.description || "-").toString());
  const id = t.id != null ? String(t.id) : "";
  return `
    <div class="tx" data-id="${id}" role="button" tabindex="0">
      <div class="tx-top">
        <div class="tx-amount ${cls}">${amount}</div>
        <div class="tx-meta">${formatDate(dateStr)}</div>
      </div>
      <div class="tx-meta">${cat}${cat ? " • " : ""}${desc}</div>
    </div>
  `;
}

function renderTxList(container, items, showEmpty = true, emptyMsg = "Belum ada transaksi.") {
  if (!container) return;
  if (!items || items.length === 0) {
    container.innerHTML = showEmpty ? `<div class="hint">${emptyMsg}</div>` : "";
    return;
  }
  container.innerHTML = items.map((t) => renderTxItem(t)).join("");
}

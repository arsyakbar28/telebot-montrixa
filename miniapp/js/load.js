/* Data loading: balance, categories, transactions, date range */

async function loadBalance() {
  if (incomeVal) incomeVal.textContent = "…";
  if (expenseVal) expenseVal.textContent = "…";
  if (balanceVal) balanceVal.textContent = "…";
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const start = formatLocalDateISO(monthStart);
  const end = formatLocalDateISO(now);
  const [overall, monthly] = await Promise.all([
    apiFetch("/api/balance"),
    apiFetch(`/api/balance?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`),
  ]);
  if (incomeVal) incomeVal.textContent = formatRp(monthly.income);
  if (expenseVal) expenseVal.textContent = formatRp(monthly.expense);
  if (balanceVal) balanceVal.textContent = formatRp(overall.balance);
}

async function loadCategories() {
  if (!categorySelect) return;
  categorySelect.innerHTML = `<option value="">Memuat...</option>`;
  const data = await apiFetch(`/api/categories?type=${encodeURIComponent(currentType)}`);
  const cats = data.categories || [];
  if (cats.length === 0) {
    categorySelect.innerHTML = `<option value="">(Tidak ada kategori)</option>`;
    return;
  }
  categorySelect.innerHTML = cats
    .map((c) => `<option value="${c.id}">${c.name}</option>`)
    .join("");
}

async function loadLast5() {
  if (lastTxList) lastTxList.innerHTML = `<div class="hint">Memuat…</div>`;
  const end = new Date();
  const start = new Date();
  start.setFullYear(start.getFullYear() - 1);
  const startStr = formatLocalDateISO(start);
  const endStr = formatLocalDateISO(end);
  const cacheBust = Date.now();
  const data = await apiFetch(`/api/transactions?start=${startStr}&end=${endStr}&limit=5&offset=0&_=${cacheBust}`);
  lastTxData = data.transactions || [];
  renderTxList(lastTxList, lastTxData, true, "Belum ada transaksi.");
}

function getDateRange() {
  let start = filterStart && filterStart.value ? filterStart.value : null;
  let end = filterEnd && filterEnd.value ? filterEnd.value : null;
  if (!start || !end) {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);
    start = formatLocalDateISO(startDate);
    end = formatLocalDateISO(endDate);
    if (filterStart) filterStart.value = start;
    if (filterEnd) filterEnd.value = end;
  }
  return { start, end };
}

async function loadTransactionList() {
  const { start, end } = getDateRange();
  if (txList) txList.innerHTML = `<div class="hint">Memuat…</div>`;
  if (txListEmpty) txListEmpty.hidden = true;
  if (txIncomeVal) txIncomeVal.textContent = "…";
  if (txExpenseVal) txExpenseVal.textContent = "…";
  const offset = txPage * TX_PAGE_SIZE;
  const [data, summary] = await Promise.all([
    apiFetch(
      `/api/transactions?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}&limit=${TX_PAGE_SIZE}&offset=${offset}`
    ),
    apiFetch(`/api/balance?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`),
  ]);
  const list = data.transactions || [];
  txTotal = data.total ?? 0;
  txListData = list;
  if (txIncomeVal) txIncomeVal.textContent = formatRp(summary.income);
  if (txExpenseVal) txExpenseVal.textContent = formatRp(summary.expense);

  if (txList) renderTxList(txList, list, false);
  if (txListEmpty) {
    txListEmpty.hidden = list.length > 0;
  }
  if (txCount) {
    txCount.textContent = `Total: ${txTotal}`;
  }

  const totalPages = Math.max(1, Math.ceil(txTotal / TX_PAGE_SIZE));
  if (txPagination) {
    txPagination.innerHTML = `
      <button type="button" id="txPrev" ${txPage <= 0 ? "disabled" : ""}>Prev</button>
      <span class="page-info">${txPage + 1} / ${totalPages}</span>
      <button type="button" id="txNext" ${txPage >= totalPages - 1 ? "disabled" : ""}>Next</button>
    `;
    const prevBtn = $("txPrev");
    const nextBtn = $("txNext");
    if (prevBtn) prevBtn.addEventListener("click", () => { txPage = Math.max(0, txPage - 1); loadTransactionList().catch(() => {}); });
    if (nextBtn) nextBtn.addEventListener("click", () => { txPage = Math.min(totalPages - 1, txPage + 1); loadTransactionList().catch(() => {}); });
  }
}

async function setDefaultDateRange() {
  let end = new Date();
  let start = new Date();
  try {
    const meta = await apiFetch("/api/transactions/meta");
    if (meta && meta.oldest_date) {
      const oldest = new Date(`${meta.oldest_date}T00:00:00`);
      if (!Number.isNaN(oldest.getTime())) start = oldest;
      else start.setDate(start.getDate() - 30);
    } else {
      start.setDate(start.getDate() - 30);
    }
    if (meta && meta.newest_date) {
      const newest = new Date(`${meta.newest_date}T00:00:00`);
      if (!Number.isNaN(newest.getTime())) end = newest;
    }
  } catch (_) {
    start.setDate(start.getDate() - 30);
  }
  if (start > end) start = new Date(end);
  if (filterStart) filterStart.value = formatLocalDateISO(start);
  if (filterEnd) filterEnd.value = formatLocalDateISO(end);
}

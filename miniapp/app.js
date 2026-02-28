/* global Telegram, Chart */

const $ = (id) => document.getElementById(id);

const statusText = $("statusText");
const envWarning = $("envWarning");
const btnClose = $("btnClose");

const viewHome = $("viewHome");
const viewAnalytic = $("viewAnalytic");
const viewTransaction = $("viewTransaction");
const viewAddTx = $("viewAddTx");
const viewTxDetail = $("viewTxDetail");

const lastTxList = $("lastTxList");
const txList = $("txList");
const txListEmpty = $("txListEmpty");
const txCount = $("txCount");
const txPagination = $("txPagination");
const linkSeeAll = $("linkSeeAll");

const incomeVal = $("incomeVal");
const expenseVal = $("expenseVal");
const balanceVal = $("balanceVal");

const btnAddIncome = $("btnAddIncome");
const btnAddExpense = $("btnAddExpense");
const btnBackAddTx = $("btnBackAddTx");
const addTxTitle = $("addTxTitle");
const addTxBanner = $("addTxBanner");
const addTxBannerLabel = $("addTxBannerLabel");
const addTxType = $("addTxType");
const amountInput = $("amountInput");
const descInput = $("descInput");
const categorySelect = $("categorySelect");
const txForm = $("txForm");
const btnSave = $("btnSave");

const filterStart = $("filterStart");
const filterEnd = $("filterEnd");
const chartCanvas = $("chartCanvas");
const chartEmpty = $("chartEmpty");
const categoryBreakdown = $("categoryBreakdown");
const breakdownEmpty = $("breakdownEmpty");
const analyticTypeIncome = $("analyticTypeIncome");
const analyticTypeExpense = $("analyticTypeExpense");
const bottomNav = $("bottomNav");
const btnBackTxDetail = $("btnBackTxDetail");
const btnEditTx = $("btnEditTx");
const btnDeleteTx = $("btnDeleteTx");
const detailDate = $("detailDate");
const detailType = $("detailType");
const detailCategory = $("detailCategory");
const detailAmount = $("detailAmount");
const detailDesc = $("detailDesc");

let lastTxData = [];
let txListData = [];
let selectedTx = null;
let selectedTxId = null;
let editingTxId = null;
let tabBeforeDetail = "home";

const fmt = new Intl.NumberFormat("id-ID");
const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
const initData = tg && tg.initData ? tg.initData : "";

let currentType = "expense";
let currentTab = "home";
let txPage = 0;
const TX_PAGE_SIZE = 10;
let txTotal = 0;
let chartInstance = null;

const PRESET_DAYS = { 7: 7, 30: 30, 0: "month" };

function setStatus(msg, kind = "muted") {
  if (!statusText) return;
  statusText.textContent = msg || "";
  statusText.style.color =
    kind === "ok"
      ? "rgba(32, 211, 162, 0.95)"
      : kind === "err"
        ? "rgba(255, 92, 115, 0.95)"
        : "rgba(255, 255, 255, 0.68)";
}

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("X-Telegram-Init-Data", initData);
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(path, { ...options, headers });
  let payload = null;
  try {
    payload = await res.json();
  } catch (_) {}
  if (!res.ok) {
    const detail = payload && (payload.detail || payload.error) ? (payload.detail || payload.error) : `HTTP ${res.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return payload;
}

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

function showView(viewId) {
  [viewHome, viewAnalytic, viewTransaction, viewAddTx, viewTxDetail].forEach((v) => {
    if (v) v.classList.remove("active");
  });
  const v = $(viewId);
  if (v) v.classList.add("active");

  const tabFromView = viewId === "viewHome" ? "home" : viewId === "viewAnalytic" ? "analytic" : viewId === "viewTransaction" ? "transaction" : "";
  document.querySelectorAll(".nav-item").forEach((el) => {
    el.classList.toggle("active", el.getAttribute("data-tab") === tabFromView);
  });

  const hideNav = viewId === "viewAddTx" || viewId === "viewTxDetail";
  const appEl = document.querySelector(".app");
  if (appEl) appEl.classList.toggle("show-add", hideNav);
}

function switchTab(tab, options = {}) {
  const { skipRefresh = false } = options;
  currentTab = tab;
  if (tab === "home") {
    showView("viewHome");
    if (!skipRefresh) {
      loadBalance().catch(() => {});
      loadLast5().catch(() => {});
    }
  } else if (tab === "analytic") {
    showView("viewAnalytic");
    if (!skipRefresh) loadAnalytics().catch(() => {});
  } else if (tab === "transaction") {
    showView("viewTransaction");
    if (!skipRefresh) loadTransactionList().catch(() => {});
  }
}

function openAddTransaction(type) {
  editingTxId = null;
  currentType = type;
  addTxType.value = type;
  if (txForm) txForm.dataset.type = type;
  if (addTxTitle) addTxTitle.textContent = type === "income" ? "Tambah Pemasukan" : "Tambah Pengeluaran";
  if (addTxBanner) {
    addTxBanner.classList.remove("income", "expense");
    addTxBanner.classList.add(type);
  }
  if (addTxBannerLabel) addTxBannerLabel.textContent = type === "income" ? "Pemasukan" : "Pengeluaran";
  amountInput.value = "";
  descInput.value = "";
  setStatus("");
  loadCategories().catch(() => {});
  showView("viewAddTx");
}

function closeAddTransaction() {
  if (editingTxId) {
    editingTxId = null;
    showView("viewTxDetail");
    return;
  }
  switchTab("home", { skipRefresh: true });
}

function fillTxDetail(tx) {
  if (!tx) return;
  const dateStr = tx.transaction_date ? String(tx.transaction_date).slice(0, 10) : "";
  if (detailDate) detailDate.textContent = formatDate(dateStr) || "-";
  if (detailType) detailType.textContent = tx.type === "income" ? "Pemasukan" : "Pengeluaran";
  if (detailCategory) detailCategory.innerHTML = renderCategoryLabel(tx.category_icon, tx.category_name, tx.type);
  if (detailAmount) {
    detailAmount.textContent = (tx.type === "income" ? "+" : "−") + formatRp(Math.abs(Number(tx.amount || 0)));
    detailAmount.className = "tx-detail-value tx-detail-amount " + (tx.type === "income" ? "income" : "expense");
  }
  if (detailDesc) detailDesc.textContent = (tx.description && tx.description !== "-") ? tx.description : "-";
}

function openTxDetail(tx) {
  selectedTx = tx;
  selectedTxId = tx.id;
  tabBeforeDetail = currentTab;
  fillTxDetail(tx);
  showView("viewTxDetail");
}

function closeTxDetail() {
  selectedTx = null;
  selectedTxId = null;
  const tab = tabBeforeDetail || "home";
  switchTab(tab, { skipRefresh: true });
}

async function loadBalance() {
  if (incomeVal) incomeVal.textContent = "…";
  if (expenseVal) expenseVal.textContent = "…";
  if (balanceVal) balanceVal.textContent = "…";
  const b = await apiFetch("/api/balance");
  if (incomeVal) incomeVal.textContent = formatRp(b.income);
  if (expenseVal) expenseVal.textContent = formatRp(b.expense);
  if (balanceVal) balanceVal.textContent = formatRp(b.balance);
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
  const offset = txPage * TX_PAGE_SIZE;
  const data = await apiFetch(
    `/api/transactions?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}&limit=${TX_PAGE_SIZE}&offset=${offset}`
  );
  const list = data.transactions || [];
  txTotal = data.total ?? 0;
  txListData = list;

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

function setAnalyticType(type) {
  currentType = type;
  if (type === "income") {
    analyticTypeIncome.classList.add("active");
    analyticTypeExpense.classList.remove("active");
  } else {
    analyticTypeExpense.classList.add("active");
    analyticTypeIncome.classList.remove("active");
  }
  loadAnalytics().catch(() => {});
}

async function loadAnalytics() {
  const { start, end } = getDateRange();
  if (chartEmpty) chartEmpty.hidden = true;
  if (categoryBreakdown) categoryBreakdown.innerHTML = `<div class="hint">Memuat…</div>`;
  if (breakdownEmpty) breakdownEmpty.hidden = true;
  const data = await apiFetch(
    `/api/analytics?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}&type=${encodeURIComponent(currentType)}`
  );

  const byDay = data.by_day || [];
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }

  if (chartCanvas) {
    const ctx = chartCanvas.getContext("2d");
    const labels = byDay.map((d) => formatDate(d.date));
    const values = byDay.map((d) => (currentType === "income" ? d.income : d.expense));

    if (chartEmpty) chartEmpty.hidden = values.length > 0;

    if (values.length > 0) {
      chartInstance = new Chart(ctx, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: currentType === "income" ? "Pemasukan" : "Pengeluaran",
              data: values,
              backgroundColor: currentType === "income" ? "rgba(32, 211, 162, 0.6)" : "rgba(255, 92, 115, 0.6)",
              borderColor: currentType === "income" ? "rgba(32, 211, 162, 0.9)" : "rgba(255, 92, 115, 0.9)",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: "rgba(255,255,255,0.08)" },
              ticks: { color: "rgba(255,255,255,0.7)" },
            },
            x: {
              grid: { display: false },
              ticks: { color: "rgba(255,255,255,0.7)", maxRotation: 45 },
            },
          },
        },
      });
    }
  }

  const byCategory = data.by_category || [];
  if (categoryBreakdown) {
    if (byCategory.length === 0) {
      categoryBreakdown.innerHTML = "";
      if (breakdownEmpty) {
        breakdownEmpty.hidden = false;
        breakdownEmpty.textContent = "Belum ada data untuk periode ini.";
      }
    } else {
      if (breakdownEmpty) breakdownEmpty.hidden = true;
      const maxPct = Math.max(...byCategory.map((c) => c.percentage), 1);
      categoryBreakdown.innerHTML = byCategory
        .map(
          (c) => `
        <div class="breakdown-item">
          <span class="breakdown-name">${renderCategoryLabel(c.category_icon, c.category_name, currentType)}</span>
          <div class="breakdown-bar-wrap">
            <div class="breakdown-bar" style="width:${c.percentage}%; background:${currentType === "income" ? "rgba(32, 211, 162, 0.7)" : "rgba(255, 92, 115, 0.7)"}"></div>
          </div>
          <span class="breakdown-pct">${formatPct(c.percentage)}</span>
        </div>
      `
        )
        .join("");
    }
  }
}

async function onSubmit(e) {
  e.preventDefault();
  setStatus("");

  const amount = getAmountDigits(amountInput.value);
  const description = (descInput.value || "").trim() || "-";
  const categoryId = Number(categorySelect.value || 0);

  if (!amount) {
    setStatus("Nominal wajib diisi.", "err");
    return;
  }
  if (!categoryId) {
    setStatus("Kategori wajib dipilih.", "err");
    return;
  }

  btnSave.disabled = true;
  setStatus("Menyimpan...");
  try {
    if (editingTxId) {
      await apiFetch(`/api/transaction/${editingTxId}`, {
        method: "PATCH",
        body: JSON.stringify({
          amount,
          description,
          category_id: categoryId,
          type: currentType,
        }),
      });
      setStatus("Transaksi diperbarui.", "ok");
      editingTxId = null;
      await Promise.all([loadBalance(), loadLast5(), loadTransactionList().catch(() => {})]);
      if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("success");
      closeTxDetail();
    } else {
      await apiFetch("/api/transaction", {
        method: "POST",
        body: JSON.stringify({
          amount,
          description,
          category_id: categoryId,
          type: currentType,
        }),
      });
      setStatus("Tersimpan.", "ok");
      amountInput.value = "";
      descInput.value = "";
      await Promise.all([loadBalance(), loadLast5()]);
      if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("success");
      closeAddTransaction();
    }
  } catch (err) {
    setStatus(err.message || "Gagal menyimpan.", "err");
    if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("error");
  } finally {
    btnSave.disabled = false;
  }
}

function setDefaultDateRange() {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 30);
  if (filterStart) filterStart.value = formatLocalDateISO(start);
  if (filterEnd) filterEnd.value = formatLocalDateISO(end);
}

function init() {
  if (tg) {
    tg.ready();
    tg.expand();
    if (btnClose) btnClose.addEventListener("click", () => tg.close());
  } else {
    if (btnClose) btnClose.hidden = true;
  }

  if (!initData) {
    if (envWarning) envWarning.hidden = false;
    setStatus("init_data tidak ada (buka dari Telegram).", "err");
    return;
  }

  document.querySelectorAll(".nav-item").forEach((el) => {
    el.addEventListener("click", () => switchTab(el.getAttribute("data-tab")));
  });

  if (btnAddIncome) btnAddIncome.addEventListener("click", () => openAddTransaction("income"));
  if (btnAddExpense) btnAddExpense.addEventListener("click", () => openAddTransaction("expense"));
  if (btnBackAddTx) btnBackAddTx.addEventListener("click", closeAddTransaction);

  if (btnBackTxDetail) btnBackTxDetail.addEventListener("click", closeTxDetail);

  if (btnEditTx) {
    btnEditTx.addEventListener("click", () => {
      if (!selectedTx) return;
      editingTxId = selectedTxId;
      currentType = selectedTx.type;
      addTxType.value = selectedTx.type;
      txForm.dataset.type = selectedTx.type;
      addTxTitle.textContent = "Edit Transaksi";
      addTxBanner.classList.remove("income", "expense");
      addTxBanner.classList.add(selectedTx.type);
      addTxBannerLabel.textContent = selectedTx.type === "income" ? "Pemasukan" : "Pengeluaran";
      amountInput.value = formatAmountInput(selectedTx.amount || "");
      descInput.value = (selectedTx.description && selectedTx.description !== "-") ? selectedTx.description : "";
      loadCategories().then(() => {
        if (categorySelect) categorySelect.value = selectedTx.category_id || "";
      }).catch(() => {});
      setStatus("");
      showView("viewAddTx");
    });
  }

  if (btnDeleteTx) {
    btnDeleteTx.addEventListener("click", async () => {
      if (!selectedTxId) return;
      if (!confirm("Yakin hapus transaksi ini?")) return;
      try {
        await apiFetch(`/api/transaction/${selectedTxId}`, { method: "DELETE" });
        if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("success");
        await Promise.all([loadBalance(), loadLast5(), loadTransactionList().catch(() => {})]);
        closeTxDetail();
      } catch (err) {
        alert(err.message || "Gagal menghapus transaksi.");
      }
    });
  }

  const mainEl = document.querySelector(".main");
  if (mainEl) {
    mainEl.addEventListener("click", (e) => {
      const row = e.target.closest(".tx[data-id]");
      if (!row) return;
      const id = (row.getAttribute("data-id") || "").trim();
      if (!id) return;
      const inLast = lastTxList && lastTxList.contains(row);
      const items = inLast ? lastTxData : txListData;
      const tx = items.find((t) => String(t.id) === id);
      if (tx) openTxDetail(tx);
    });
  }

  if (linkSeeAll) {
    linkSeeAll.addEventListener("click", (e) => {
      e.preventDefault();
      switchTab("transaction");
    });
  }

  if (analyticTypeIncome) analyticTypeIncome.addEventListener("click", () => setAnalyticType("income"));
  if (analyticTypeExpense) analyticTypeExpense.addEventListener("click", () => setAnalyticType("expense"));

  document.querySelectorAll(".preset-buttons button").forEach((btn) => {
    btn.addEventListener("click", () => {
      const days = parseInt(btn.getAttribute("data-days"), 10);
      const end = new Date();
      const start = new Date();
      if (days === 0) {
        start.setDate(1);
        if (filterEnd) filterEnd.value = formatLocalDateISO(end);
        if (filterStart) filterStart.value = formatLocalDateISO(start);
      } else {
        start.setDate(start.getDate() - days);
        if (filterStart) filterStart.value = formatLocalDateISO(start);
        if (filterEnd) filterEnd.value = formatLocalDateISO(end);
      }
      txPage = 0;
      loadTransactionList().catch(() => {});
    });
  });

  if (filterStart && filterEnd) {
    filterStart.addEventListener("change", () => { txPage = 0; loadTransactionList().catch(() => {}); });
    filterEnd.addEventListener("change", () => { txPage = 0; loadTransactionList().catch(() => {}); });
  }

  if (amountInput) {
    amountInput.addEventListener("input", () => {
      amountInput.value = formatAmountInput(amountInput.value);
    });
  }

  if (txForm) txForm.addEventListener("submit", onSubmit);

  setDefaultDateRange();
  Promise.all([loadBalance(), loadLast5()])
    .then(() => setStatus(""))
    .catch((e) => setStatus(e.message, "err"));
}

init();

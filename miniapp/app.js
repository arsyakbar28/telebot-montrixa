/* global Telegram */

const $ = (id) => document.getElementById(id);

const statusText = $("statusText");
const envWarning = $("envWarning");
const btnClose = $("btnClose");

const typeIncome = $("typeIncome");
const typeExpense = $("typeExpense");
const amountInput = $("amountInput");
const descInput = $("descInput");
const categorySelect = $("categorySelect");
const periodSelect = $("periodSelect");
const txList = $("txList");

const incomeVal = $("incomeVal");
const expenseVal = $("expenseVal");
const balanceVal = $("balanceVal");

const txForm = $("txForm");
const btnSave = $("btnSave");

const fmt = new Intl.NumberFormat("id-ID");

const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
const initData = tg && tg.initData ? tg.initData : "";

let currentType = "expense";

function setStatus(msg, kind = "muted") {
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
    throw new Error(detail);
  }
  return payload;
}

function renderTxList(items) {
  if (!items || items.length === 0) {
    txList.innerHTML = `<div class="hint">Belum ada transaksi di periode ini.</div>`;
    return;
  }
  txList.innerHTML = items
    .map((t) => {
      const sign = t.type === "income" ? "+" : "-";
      const amount = `${sign}${fmt.format(Number(t.amount || 0))}`;
      const cls = t.type === "income" ? "income" : "expense";
      const cat = `${t.category_icon || ""} ${t.category_name || ""}`.trim();
      const date = t.transaction_date ? String(t.transaction_date).slice(0, 10) : "";
      const desc = (t.description || "-").toString();
      return `
        <div class="tx">
          <div class="tx-top">
            <div class="tx-amount ${cls}">${amount}</div>
            <div class="tx-meta">${date}</div>
          </div>
          <div class="tx-meta">${cat}${cat ? " • " : ""}${desc}</div>
        </div>
      `;
    })
    .join("");
}

async function loadBalance() {
  const b = await apiFetch("/api/balance");
  incomeVal.textContent = fmt.format(Number(b.income || 0));
  expenseVal.textContent = fmt.format(Number(b.expense || 0));
  balanceVal.textContent = fmt.format(Number(b.balance || 0));
}

async function loadCategories() {
  categorySelect.innerHTML = `<option>Memuat...</option>`;
  const data = await apiFetch(`/api/categories?type=${encodeURIComponent(currentType)}`);
  const cats = data.categories || [];
  if (cats.length === 0) {
    categorySelect.innerHTML = `<option value="">(Tidak ada kategori)</option>`;
    return;
  }
  categorySelect.innerHTML = cats
    .map((c) => `<option value="${c.id}">${(c.icon ? c.icon + " " : "") + c.name}</option>`)
    .join("");
}

async function loadTransactions() {
  const p = periodSelect.value || "30d";
  const data = await apiFetch(`/api/transactions?period=${encodeURIComponent(p)}`);
  renderTxList(data.transactions || []);
}

function setType(type) {
  currentType = type;
  if (type === "income") {
    typeIncome.classList.add("active");
    typeExpense.classList.remove("active");
  } else {
    typeExpense.classList.add("active");
    typeIncome.classList.remove("active");
  }
  loadCategories().catch((e) => setStatus(e.message, "err"));
}

async function onSubmit(e) {
  e.preventDefault();
  setStatus("");

  const amount = (amountInput.value || "").trim();
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
    await Promise.all([loadBalance(), loadTransactions()]);
    if (tg) tg.HapticFeedback && tg.HapticFeedback.notificationOccurred("success");
  } catch (err) {
    setStatus(err.message || "Gagal menyimpan.", "err");
    if (tg) tg.HapticFeedback && tg.HapticFeedback.notificationOccurred("error");
  } finally {
    btnSave.disabled = false;
  }
}

function init() {
  if (tg) {
    tg.ready();
    tg.expand();
    btnClose.addEventListener("click", () => tg.close());
  } else {
    btnClose.hidden = true;
  }

  if (!initData) {
    envWarning.hidden = false;
    setStatus("init_data tidak ada (buka dari Telegram).", "err");
    return;
  }

  typeIncome.addEventListener("click", () => setType("income"));
  typeExpense.addEventListener("click", () => setType("expense"));
  periodSelect.addEventListener("change", () => loadTransactions().catch((e) => setStatus(e.message, "err")));
  txForm.addEventListener("submit", onSubmit);

  Promise.all([loadBalance(), loadCategories(), loadTransactions()])
    .then(() => setStatus(""))
    .catch((e) => setStatus(e.message, "err"));
}

init();


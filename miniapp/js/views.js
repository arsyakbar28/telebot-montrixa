/* View switching and transaction detail */

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
  if (detailDate) detailDate.textContent = formatDetailDateTime(tx);
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

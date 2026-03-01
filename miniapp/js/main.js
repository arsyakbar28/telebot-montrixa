/* global Chart */
/* Status, init, and event binding */

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

  function handleTxRowClick(row) {
    if (!row) return;
    const id = (row.getAttribute("data-id") || "").trim();
    if (!id) return;
    const inLast = lastTxList && lastTxList.contains(row);
    const items = inLast ? lastTxData : txListData;
    const tx = items.find((t) => String(t.id) === id);
    if (tx) openTxDetail(tx);
  }

  const mainEl = document.querySelector(".main");
  if (mainEl) {
    mainEl.addEventListener("click", (e) => {
      const row = e.target.closest(".tx");
      handleTxRowClick(row);
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
      if (!PRESET_DAYS[days]) return;
      const end = new Date();
      const start = new Date();
      start.setDate(start.getDate() - days);
      if (filterStart) filterStart.value = formatLocalDateISO(start);
      if (filterEnd) filterEnd.value = formatLocalDateISO(end);
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

  setDefaultDateRange()
    .then(() => Promise.all([loadBalance(), loadLast5()]))
    .then(() => setStatus(""))
    .catch((e) => setStatus(e.message, "err"));
}

init();

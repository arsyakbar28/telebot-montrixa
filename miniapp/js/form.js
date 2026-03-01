/* Add/Edit transaction form submit */

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

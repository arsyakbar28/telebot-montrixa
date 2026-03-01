/* global Chart */
/* Analytics view: chart and category breakdown */

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

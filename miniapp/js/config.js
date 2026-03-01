/* global Telegram */
/* Config, DOM refs, and constants */

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
const txIncomeVal = $("txIncomeVal");
const txExpenseVal = $("txExpenseVal");
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

const fmt = new Intl.NumberFormat("id-ID");
const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
const initData = tg && tg.initData ? tg.initData : "";

const TX_PAGE_SIZE = 10;
const PRESET_DAYS = { 7: 7, 30: 30 };

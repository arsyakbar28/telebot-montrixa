/* Mutable application state */

let lastTxData = [];
let txListData = [];
let selectedTx = null;
let selectedTxId = null;
let editingTxId = null;
let tabBeforeDetail = "home";

let currentType = "expense";
let currentTab = "home";
let txPage = 0;
let txTotal = 0;
let chartInstance = null;

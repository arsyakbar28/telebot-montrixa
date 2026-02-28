# Montrixa - Smart Way to Control Your Money

Bot Telegram untuk pencatatan keuangan pribadi dengan fitur lengkap: tracking pemasukan/pengeluaran, kategori, laporan statistik, budget planning, dan transaksi berulang.

## ✨ Fitur

### 💰 Pencatatan Transaksi
- Catat pemasukan dan pengeluaran dengan mudah
- Kategori otomatis (Income: Gaji, Bonus, Investasi | Expense: Makanan, Transport, dll)
- Tambah kategori custom sesuai kebutuhan
- Edit dan hapus transaksi

### 📊 Laporan & Analisis
- Summary bulanan otomatis
- Breakdown pengeluaran per kategori
- Grafik dan visualisasi data
- Export data ke CSV
- Perbandingan dengan periode sebelumnya

### 💳 Budget Planning
- Set budget per kategori (harian/mingguan/bulanan)
- Real-time tracking penggunaan budget
- Alert otomatis saat budget mencapai 75%, 90%, dan 100%
- Monitor multiple budgets

### 🔄 Transaksi Berulang
- Setup transaksi otomatis (subscription, gaji, sewa, dll)
- Frekuensi: harian, mingguan, bulanan
- Pause/Resume transaksi berulang
- Notifikasi saat transaksi dijalankan

## 🚀 Instalasi

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Telegram Bot Token (dari [@BotFather](https://t.me/botfather))

### 1. Clone Repository
```bash
git clone <repository-url>
cd Montrixa
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database
```bash
# Buat database MySQL
mysql -u root -p
CREATE DATABASE montrixa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Run migration
python migrations/run_migration.py
```

### 5. Configuration
```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env dengan konfigurasi Anda
nano .env
```

Isi file `.env`:
```env
# Telegram Bot Token (dari @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# MySQL Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=montrixa
DB_USER=root
DB_PASSWORD=your_password

# App Settings
TIMEZONE=Asia/Jakarta
DEFAULT_CURRENCY=IDR
LOG_LEVEL=INFO
```

### 6. Run Bot
```bash
python bot.py
```

Bot akan berjalan dan siap menerima perintah! 🎉

## 🧩 Telegram Mini App (Web App)

Montrixa mendukung Mini App (Web App) untuk input yang lebih nyaman (form catat transaksi + saldo + riwayat).

### Jalankan Mini App API (FastAPI)

1) Install dependency:

```bash
pip install -r requirements.txt
```

2) Jalankan API server:

```bash
python run_miniapp_api.py
```

Secara default API akan jalan di `http://127.0.0.1:8000` dan juga otomatis melayani file Mini App dari folder `miniapp/`.

### Konfigurasi `.env`

Tambahkan:

```env
# URL publik Mini App (harus HTTPS untuk produksi)
MINIAPP_URL=https://domain-anda.com/

# Opsional (untuk run lokal API)
API_HOST=127.0.0.1
API_PORT=8000

# Opsional: batas usia init_data (detik), default 86400 (1 hari)
MINIAPP_INITDATA_MAX_AGE_SECONDS=86400
```

Jika `MINIAPP_URL` sudah diisi, menu bot akan menampilkan tombol **Buka App**.

## 📱 Cara Penggunaan

### Commands Dasar

**Mulai menggunakan bot:**
```
/start - Registrasi dan mulai menggunakan bot
/help - Tampilkan panduan lengkap
/menu - Tampilkan menu utama
```

### 💰 Transaksi

**Catat pemasukan:**
```
/income 5000000 gaji bulanan
/income 1000000 bonus project
```

**Catat pengeluaran:**
```
/expense 50000 makan siang
/expense 100000 bensin
```

**Lihat transaksi:**
```
/list - Transaksi hari ini
/history - Riwayat transaksi
/balance - Cek saldo total
```

### 📁 Kategori

```
/categories - Lihat semua kategori
/addcategory Hobby expense - Tambah kategori pengeluaran
/addcategory Freelance income - Tambah kategori pemasukan
```

### 💳 Budget

```
/budget - Lihat semua budget
/setbudget Makanan 1000000 bulanan - Set budget bulanan
/budgetstatus - Status penggunaan budget
```

### 🔄 Transaksi Berulang

```
/recurring - Lihat transaksi berulang
/addrecurring expense 1000000 "Sewa kost" bulanan
/addrecurring income 5000000 Gaji bulanan
```

### 📊 Laporan

```
/summary - Ringkasan bulan ini
/report - Laporan lengkap dengan grafik
/export - Export data ke CSV
```

## 🏗️ Arsitektur

```
montrixa/
├── config/          # Konfigurasi aplikasi dan database
├── models/          # Data models (User, Transaction, Category, dll)
├── services/        # Business logic layer
├── handlers/        # Telegram bot command handlers
├── utils/           # Helper functions (formatters, validators, dll)
├── jobs/            # Background jobs (recurring, alerts)
├── migrations/      # Database migrations
├── bot.py          # Main entry point
└── requirements.txt
```

### Database Schema

- **users** - Data user Telegram
- **categories** - Kategori transaksi
- **transactions** - Semua transaksi
- **budgets** - Budget planning
- **recurring_transactions** - Transaksi berulang
- **budget_alerts** - Log alert budget

## 🔧 Development

### Setup Development Environment

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest

# Code formatting
black .

# Linting
flake8
```

### Database Migration

```bash
# Run initial migration
python migrations/run_migration.py

# Check database
mysql -u root -p montrixa
SHOW TABLES;
```

## 📊 Background Jobs

Bot menjalankan 2 background jobs:

1. **Recurring Transactions** - Setiap 1 jam
   - Memproses transaksi berulang yang sudah jatuh tempo
   - Membuat transaksi baru secara otomatis

2. **Budget Alerts** - Setiap 6 jam
   - Mengecek status semua budget
   - Mengirim notifikasi jika budget mencapai threshold

## 🐛 Troubleshooting

### Bot tidak merespon
- Cek TOKEN di `.env` sudah benar
- Pastikan bot sudah running dengan `python bot.py`
- Lihat log error di `montrixa.log`

### Database error
- Pastikan MySQL sudah running
- Cek kredensial database di `.env`
- Run migration ulang jika perlu

### Import error
- Pastikan virtual environment aktif
- Install ulang dependencies: `pip install -r requirements.txt`

## 📄 License

MIT License - Feel free to use for personal or commercial projects

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

Untuk pertanyaan atau bug report, silakan buat issue di repository ini.

---

**Montrixa** - Kelola keuangan Anda dengan mudah! 💰✨
# telebot-montrixa

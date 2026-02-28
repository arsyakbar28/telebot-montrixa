# Panduan Instalasi Montrixa

Panduan lengkap untuk menginstall dan menjalankan Montrixa Bot.

## Persyaratan Sistem

### Software yang Dibutuhkan
- Python 3.8 atau lebih tinggi
- MySQL 8.0 atau lebih tinggi
- pip (Python package manager)
- Git (opsional, untuk clone repository)

### Telegram Requirements
- Akun Telegram
- Bot Token dari [@BotFather](https://t.me/botfather)

## Langkah Instalasi

### 1. Persiapan

#### Install Python
**Windows:**
Download dari [python.org](https://www.python.org/downloads/) dan install.
Pastikan checklist "Add Python to PATH".

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
brew install python3
```

#### Install MySQL
**Windows:**
Download MySQL Installer dari [mysql.com](https://dev.mysql.com/downloads/installer/)

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### 2. Buat Telegram Bot

1. Buka Telegram dan cari [@BotFather](https://t.me/botfather)
2. Kirim `/newbot`
3. Ikuti instruksi untuk memberi nama bot
4. Simpan TOKEN yang diberikan (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 3. Setup Project

#### Clone atau Download Project
```bash
# Jika menggunakan Git
git clone <repository-url>
cd Montrixa

# Atau download ZIP dan extract
```

#### Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database

#### Buat Database MySQL
```bash
# Login ke MySQL
mysql -u root -p

# Buat database
CREATE DATABASE montrixa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Buat user khusus (opsional tapi recommended)
CREATE USER 'montrixa_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON montrixa.* TO 'montrixa_user'@'localhost';
FLUSH PRIVILEGES;

EXIT;
```

#### Run Migration
```bash
python migrations/run_migration.py
```

Output yang diharapkan:
```
============================================================
Montrixa Database Migration
============================================================
Executed: CREATE DATABASE IF NOT EXISTS montrixa...
Executed: CREATE TABLE IF NOT EXISTS users...
...
✅ Database migration completed successfully!
```

### 5. Configuration

#### Copy Template .env
```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

#### Edit File .env
Buka `.env` dengan text editor dan isi:

```env
# Telegram Bot Token
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# MySQL Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=montrixa
DB_USER=montrixa_user
DB_PASSWORD=your_password

# App Settings
TIMEZONE=Asia/Jakarta
DEFAULT_CURRENCY=IDR
LOG_LEVEL=INFO

# Optional Settings
MAX_TRANSACTIONS_PER_PAGE=10
CHART_DPI=100
EXPORT_FORMAT=csv
```

**Important:** Ganti `TELEGRAM_BOT_TOKEN` dengan token dari BotFather!

### 6. Test Koneksi Database

```bash
python -c "from config.database import DatabaseConnection; DatabaseConnection.get_connection(); print('✅ Database connection successful!')"
```

### 7. Run Bot

```bash
python bot.py
```

Output yang diharapkan:
```
2024-02-13 10:00:00 - __main__ - INFO - Starting Montrixa Bot...
2024-02-13 10:00:00 - __main__ - INFO - Scheduler started with recurring and budget alert jobs
2024-02-13 10:00:00 - __main__ - INFO - Bot started successfully! Press Ctrl+C to stop.
```

### 8. Test Bot

1. Buka Telegram
2. Cari bot Anda (nama yang Anda buat di BotFather)
3. Kirim `/start`
4. Bot harus merespon dengan welcome message!

## Troubleshooting

### Bot tidak merespon

**Cek token:**
```bash
# Lihat token di .env
cat .env | grep TELEGRAM_BOT_TOKEN
```

**Pastikan bot running:**
```bash
# Cek process
ps aux | grep bot.py
```

### Database Connection Error

**Test MySQL connection:**
```bash
mysql -u montrixa_user -p -h localhost montrixa
```

**Cek MySQL service:**
```bash
# Linux
sudo systemctl status mysql

# macOS
brew services list | grep mysql

# Windows
# Cek di Services app
```

### Import Error / ModuleNotFoundError

**Pastikan virtual environment aktif:**
```bash
# Cek path Python
which python  # Linux/macOS
where python  # Windows

# Harus menunjuk ke venv/bin/python atau venv\Scripts\python.exe
```

**Install ulang dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Permission Denied (Linux/macOS)

```bash
chmod +x bot.py
chmod +x migrations/run_migration.py
```

### Port Already in Use

Jika MySQL port (3306) sudah digunakan:
```bash
# Ganti port di .env
DB_PORT=3307

# Atau stop service yang menggunakan port
sudo lsof -i :3306
sudo kill -9 <PID>
```

## Production Deployment

**Deploy di VPS (Bot + Mini App dengan Nginx & SSL):** lihat [VPS_DEPLOY.md](VPS_DEPLOY.md) untuk panduan step-by-step.

### Systemd Service (Linux)

Buat file `/etc/systemd/system/montrixa.service`:

```ini
[Unit]
Description=Montrixa Telegram Bot
After=network.target mysql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/Montrixa
Environment="PATH=/path/to/Montrixa/venv/bin"
ExecStart=/path/to/Montrixa/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable dan start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable montrixa
sudo systemctl start montrixa
sudo systemctl status montrixa
```

### PM2 (Alternative)

```bash
# Install PM2
npm install -g pm2

# Start bot
pm2 start bot.py --name montrixa --interpreter python3

# Auto-start on boot
pm2 startup
pm2 save
```

### Docker (Alternative)

Coming soon...

## Update Bot

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt

# Run migration (if any)
python migrations/run_migration.py

# Restart bot
# Ctrl+C and python bot.py
# Or: sudo systemctl restart montrixa
```

## Backup Database

```bash
# Backup
mysqldump -u montrixa_user -p montrixa > backup_$(date +%Y%m%d).sql

# Restore
mysql -u montrixa_user -p montrixa < backup_20240213.sql
```

## Uninstall

```bash
# Stop bot
# Ctrl+C or sudo systemctl stop montrixa

# Drop database
mysql -u root -p -e "DROP DATABASE montrixa;"

# Remove files
cd ..
rm -rf Montrixa

# Deactivate venv
deactivate
```

## Support

Jika mengalami masalah:
1. Cek log file: `montrixa.log`
2. Lihat error di terminal
3. Buat issue di repository
4. Hubungi developer

---

Selamat! Montrixa Bot sudah siap digunakan! 🎉

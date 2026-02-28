# Quick Start Guide - Montrixa Bot

Panduan cepat untuk menjalankan Montrixa Bot dalam 5 menit!

## Prerequisites
✅ Python 3.8+  
✅ MySQL 8.0+  
✅ Telegram Bot Token (dari [@BotFather](https://t.me/botfather))

## Langkah Cepat

### 1. Setup Virtual Environment & Install Dependencies
```bash
cd Montrixa
python -m venv venv
source venv/bin/activate  # Linux/Mac | venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

### 2. Setup Database
```bash
# Login ke MySQL
mysql -u root -p

# Di MySQL prompt:
CREATE DATABASE montrixa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Run migration
python migrations/run_migration.py
```

### 3. Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env dan isi:
# - TELEGRAM_BOT_TOKEN (dari @BotFather)
# - DB_PASSWORD (password MySQL Anda)
nano .env
```

### 4. Run Bot
```bash
python bot.py
```

### 5. Test Bot
1. Buka Telegram
2. Cari bot Anda
3. Kirim `/start`
4. Selamat! Bot sudah jalan! 🎉

## Perintah Pertama

Coba perintah ini untuk mulai menggunakan bot:

```
/income 5000000 gaji bulanan
/expense 50000 makan siang
/summary
```

## Troubleshooting

**Bot tidak merespon?**
- Cek token di `.env` sudah benar
- Pastikan `python bot.py` masih running
- Lihat error di console atau `montrixa.log`

**Database error?**
- Pastikan MySQL running
- Cek kredensial di `.env`
- Test: `mysql -u root -p montrixa`

## Dokumentasi Lengkap

📖 [README.md](README.md) - Panduan lengkap  
📖 [INSTALL.md](INSTALL.md) - Instalasi detail  

## Support

Butuh bantuan? Buat issue di repository atau hubungi developer.

---

**Montrixa** - Kelola keuangan Anda dengan mudah! 💰

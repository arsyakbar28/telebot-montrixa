# Deploy Montrixa di VPS (Step by Step)

Panduan menjalankan **Bot Telegram** dan **Mini App API** di VPS (Ubuntu 22.04 / Debian 11) dengan Nginx + SSL, supaya jalan terus (systemd) dan Mini App bisa diakses lewat HTTPS.

---

## Yang akan dijalankan

| Layanan        | Port (internal) | Fungsi                                      |
|----------------|------------------|---------------------------------------------|
| Montrixa Bot   | -                | Telegram polling, menu, conversation        |
| Montrixa API   | 8000             | Mini App backend + serve file Mini App     |
| Nginx          | 80, 443          | Reverse proxy + SSL ke API                  |

User buka Mini App lewat tombol "Buka App" di bot → Telegram buka URL `https://domain-anda.com` → Nginx meneruskan ke API di port 8000.

---

## 1. Persiapan VPS

### 1.1 Login SSH

```bash
ssh root@IP_VPS_ANDA
# atau
ssh ubuntu@IP_VPS_ANDA
```

### 1.2 Update sistem

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 (Opsional) Buat user khusus, jangan pakai root

```bash
adduser montrixa
usermod -aG sudo montrixa
su - montrixa
```

Sisa langkah bisa jalan sebagai `root` atau user `montrixa`. Ganti `montrixa` dengan username Anda kalau beda.

---

## 2. Install dependency

### 2.1 Python 3 + venv + pip

```bash
sudo apt install -y python3 python3-pip python3-venv
python3 --version   # minimal 3.8
```

### 2.2 MySQL

```bash
sudo apt install -y mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
sudo mysql_secure_installation
```

Ikuti prompt (password root, hapus user anon, disable login remote root, dll).

### 2.3 Nginx (untuk reverse proxy + SSL)

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
```

### 2.4 Certbot (untuk HTTPS)

```bash
sudo apt install -y certbot python3-certbot-nginx
```

---

## 3. Setup database MySQL

```bash
sudo mysql -u root -p
```

Di MySQL:

```sql
CREATE DATABASE montrixa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'montrixa_user'@'localhost' IDENTIFIED BY 'GANTI_PASSWORD_KUAT';
GRANT ALL PRIVILEGES ON montrixa.* TO 'montrixa_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Catat: `montrixa_user` dan password-nya untuk dipakai di `.env`.

---

## 4. Clone & setup project

### 4.1 Clone (atau upload project)

```bash
cd /opt
sudo git clone https://github.com/USER_ANDA/Montrixa.git
# atau upload lewat scp/sftp ke /opt/Montrixa
sudo chown -R $USER:$USER /opt/Montrixa
cd /opt/Montrixa
```

Kalau pakai path lain (misal `/home/montrixa/Montrixa`), nanti sesuaikan di bagian systemd dan Nginx.

### 4.2 Virtual environment & dependency

```bash
cd /opt/Montrixa
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 File .env

```bash
cp .env.example .env
nano .env
```

Isi minimal (sesuaikan dengan VPS Anda):

```env
# Bot
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHI...

# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=montrixa
DB_USER=montrixa_user
DB_PASSWORD=GANTI_PASSWORD_KUAT

# App
TIMEZONE=Asia/Jakarta
DEFAULT_CURRENCY=IDR
LOG_LEVEL=INFO

# Mini App – API hanya listen lokal, Nginx yang terima dari luar
API_HOST=127.0.0.1
API_PORT=8000

# URL publik Mini App (pakai domain yang akan dipasang SSL)
# Ganti dengan domain Anda, harus HTTPS
MINIAPP_URL=https://montrixa.domain.com/
```

Simpan (Ctrl+O, Enter, Ctrl+X di nano).

### 4.4 Migrasi database

```bash
source venv/bin/activate
python migrations/run_migration.py
```

Pastikan ada pesan sukses (mis. "Database migration completed successfully!").

---

## 5. Systemd: Bot dan API jalan terus

Kedua service jalan terpisah: satu untuk bot, satu untuk Mini App API.

### 5.1 Service Bot

```bash
sudo nano /etc/systemd/system/montrixa-bot.service
```

Isi (sesuaikan `User` dan `WorkingDirectory` kalau path beda):

```ini
[Unit]
Description=Montrixa Telegram Bot
After=network.target mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/Montrixa
Environment="PATH=/opt/Montrixa/venv/bin"
ExecStart=/opt/Montrixa/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.2 Service Mini App API

```bash
sudo nano /etc/systemd/system/montrixa-api.service
```

Isi:

```ini
[Unit]
Description=Montrixa Mini App API
After=network.target mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/Montrixa
Environment="PATH=/opt/Montrixa/venv/bin"
ExecStart=/opt/Montrixa/venv/bin/python run_miniapp_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.3 Aktifkan & jalankan

```bash
sudo systemctl daemon-reload
sudo systemctl enable montrixa-bot montrixa-api
sudo systemctl start montrixa-bot montrixa-api
sudo systemctl status montrixa-bot montrixa-api
```

Keduanya harus `active (running)`. Cek log:

```bash
sudo journalctl -u montrixa-bot -f
sudo journalctl -u montrixa-api -f
```

---

## 6. Domain & Nginx (HTTPS)

Mini App **harus** diakses lewat HTTPS. Nginx dipakai untuk terima koneksi dari internet lalu forward ke API di port 8000.

### 6.1 Arahkan domain ke IP VPS

Di pengelola DNS (Cloudflare, Namecheap, dll):

- Buat **A record**: `montrixa.domain.com` (atau `domain.com`) → IP VPS Anda.

Tunggu propagasi (beberapa menit–jam).

### 6.2 Konfigurasi Nginx

```bash
sudo nano /etc/nginx/sites-available/montrixa
```

Ganti `montrixa.domain.com` dengan domain Anda:

```nginx
server {
    listen 80;
    server_name montrixa.domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Aktifkan site:

```bash
sudo ln -s /etc/nginx/sites-available/montrixa /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6.3 Pasang SSL (Certbot)

```bash
sudo certbot --nginx -d montrixa.domain.com
```

Ikuti prompt (email, setuju terms). Setelah selesai, Nginx otomatis pakai HTTPS dan Certbot mengatur perpanjangan.

### 6.4 Pastikan MINIAPP_URL pakai HTTPS

Di `.env` harus:

```env
MINIAPP_URL=https://montrixa.domain.com/
```

Lalu restart API supaya baca env baru:

```bash
sudo systemctl restart montrixa-api
```

---

## 7. Firewall (opsional tapi disarankan)

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
sudo ufw status
```

Port 22 (SSH), 80 (HTTP), 443 (HTTPS) terbuka. Port 8000 **tidak** perlu dibuka ke internet karena hanya Nginx yang akses ke 127.0.0.1:8000.

---

## 8. Cek jalan atau tidak

### 8.1 Bot

- Buka Telegram → cari bot Anda → `/start`
- Menu harus muncul; kalau `MINIAPP_URL` sudah diisi, tombol **Buka App** ikut muncul.

### 8.2 Mini App

- Di bot, klik **Buka App**
- Harus terbuka halaman web (saldo, form transaksi, riwayat)
- Kalau blank/error: cek log API (`journalctl -u montrixa-api -f`) dan pastikan Nginx tidak error (`sudo nginx -t` dan cek `/var/log/nginx/error.log`).

### 8.3 API dari server (tes lokal)

```bash
curl -s http://127.0.0.1:8000/api/health
```

Harus dapat response `{"ok":true}`.

---

## 9. Ringkasan perintah berguna

| Tujuan              | Perintah |
|---------------------|----------|
| Lihat status        | `sudo systemctl status montrixa-bot montrixa-api` |
| Restart bot         | `sudo systemctl restart montrixa-bot`             |
| Restart API         | `sudo systemctl restart montrixa-api`             |
| Log bot             | `sudo journalctl -u montrixa-bot -f`              |
| Log API             | `sudo journalctl -u montrixa-api -f`              |
| Log aplikasi        | `tail -f /opt/Montrixa/montrixa.log`              |

---

## 10. Troubleshooting singkat

- **Bot tidak reply**  
  Cek token di `.env`, cek log: `journalctl -u montrixa-bot -f`.

- **"Buka App" tidak muncul**  
  Pastikan `.env` ada `MINIAPP_URL=https://...` dan tidak kosong, lalu restart bot.

- **Mini App blank / 502**  
  Pastikan `montrixa-api` jalan (`systemctl status montrixa-api`), port 8000 listen (`ss -tlnp | grep 8000`), dan Nginx `proxy_pass` ke `http://127.0.0.1:8000`.

- **502 Bad Gateway**  
  Restart API: `sudo systemctl restart montrixa-api`. Cek `montrixa.log` dan `journalctl -u montrixa-api`.

- **Database error**  
  Cek MySQL jalan: `sudo systemctl status mysql`. Cek user/password di `.env` sama dengan yang di MySQL.

Dengan langkah di atas, Anda **run 2 proses di VPS** (bot + API), dan Mini App diakses lewat HTTPS via Nginx.

"""Start and help command handlers."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import authenticated, error_handler
from utils.keyboards import Keyboards
import logging

logger = logging.getLogger(__name__)


@error_handler
@authenticated
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /start command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    welcome_message = f"""
Selamat datang di Montrixa, {user.first_name}!

Bot untuk pencatatan keuangan pribadi.

FITUR UTAMA:
• Catat pemasukan & pengeluaran
• Laporan keuangan otomatis
• Budget planning & alerts
• Transaksi berulang
• Analisis spending

CARA CEPAT:
• /income 500000 gaji - Catat pemasukan
• /expense 50000 makan - Catat pengeluaran
• /summary - Lihat ringkasan bulan ini
• /help - Lihat semua perintah

Gunakan menu di bawah untuk navigasi:
"""
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=Keyboards.main_menu()
    )


@error_handler
@authenticated
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /help command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    help_message = """
PANDUAN PENGGUNAAN MONTRIXA

TRANSAKSI:
• /income [jumlah] [keterangan] - Catat pemasukan
  Contoh: /income 5000000 gaji bulanan
• /expense [jumlah] [keterangan] - Catat pengeluaran
  Contoh: /expense 50000 makan siang
• /list - Lihat transaksi hari ini
• /history - Riwayat transaksi
• /balance - Cek saldo
• /delete - Hapus transaksi
• /undo - Hapus transaksi terakhir

KATEGORI:
• /categories - Lihat semua kategori
• /addcategory [nama] [tipe] - Tambah kategori baru
  Contoh: /addcategory Hobby expense

BUDGET:
• /budget - Lihat semua budget
• /setbudget - Atur budget baru
• /budgetstatus - Status budget saat ini

BERULANG:
• /recurring - Lihat transaksi berulang
• /addrecurring - Tambah transaksi berulang

LAPORAN:
• /summary - Ringkasan bulan ini
• /report - Laporan lengkap
• /export - Export data ke CSV

LAINNYA:
• /menu - Tampilkan menu utama
• /help - Tampilkan panduan ini

Tips: Gunakan menu inline untuk navigasi lebih mudah.
"""
    
    await update.message.reply_text(help_message)


@error_handler
@authenticated
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /menu command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    await update.message.reply_text(
        "MENU UTAMA MONTRIXA\n\nPilih menu yang Anda inginkan:",
        reply_markup=Keyboards.main_menu()
    )

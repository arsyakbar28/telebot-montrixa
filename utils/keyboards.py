"""Keyboard layouts for bot interface."""

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)
from typing import List, Any
from config.settings import Settings


class Keyboards:
    """Utility class for creating keyboard layouts."""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Create main menu keyboard.
        
        Returns:
            InlineKeyboardMarkup with main menu options
        """
        keyboard = []

        if Settings.MINIAPP_URL:
            keyboard.append(
                [InlineKeyboardButton("Buka App", web_app=WebAppInfo(url=Settings.MINIAPP_URL))]
            )

        keyboard += [
            [
                InlineKeyboardButton("Cek Saldo Sekarang", callback_data="menu_saldo"),
            ],
            [
                InlineKeyboardButton("Pemasukan", callback_data="menu_income"),
                InlineKeyboardButton("Pengeluaran", callback_data="menu_expense"),
            ],
            [
                InlineKeyboardButton("Laporan", callback_data="menu_report"),
                InlineKeyboardButton("Kategori", callback_data="menu_categories"),
            ],
            [
                InlineKeyboardButton("Budget", callback_data="menu_budget"),
                InlineKeyboardButton("Berulang", callback_data="menu_recurring"),
            ],
            [
                InlineKeyboardButton("Riwayat", callback_data="menu_history"),
                InlineKeyboardButton("Bantuan", callback_data="menu_help"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def category_selection(categories: List[Any], trans_type: str, action: str = "select") -> InlineKeyboardMarkup:
        """Create category selection keyboard.
        
        Args:
            categories: List of Category objects
            trans_type: Transaction type ('income' or 'expense')
            action: Action prefix for callback data
            
        Returns:
            InlineKeyboardMarkup with category options
        """
        keyboard = []
        row = []
        
        for i, category in enumerate(categories):
            button = InlineKeyboardButton(
                category.name,
                callback_data=f"{action}_cat_{category.id}"
            )
            row.append(button)
            
            # 2 buttons per row
            if len(row) == 2 or i == len(categories) - 1:
                keyboard.append(row)
                row = []
        
        # Add cancel button
        keyboard.append([InlineKeyboardButton("❌ Batal", callback_data="cancel")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def budget_period_selection() -> InlineKeyboardMarkup:
        """Create budget period selection keyboard.
        
        Returns:
            InlineKeyboardMarkup with period options
        """
        keyboard = [
            [
                InlineKeyboardButton("Harian", callback_data="period_daily"),
                InlineKeyboardButton("Mingguan", callback_data="period_weekly"),
            ],
            [
                InlineKeyboardButton("Bulanan", callback_data="period_monthly"),
            ],
            [
                InlineKeyboardButton("❌ Batal", callback_data="cancel"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirmation(action: str, item_id: int) -> InlineKeyboardMarkup:
        """Create confirmation keyboard.
        
        Args:
            action: Action to confirm (e.g., 'delete', 'pause')
            item_id: ID of item to act on
            
        Returns:
            InlineKeyboardMarkup with confirmation options
        """
        keyboard = [
            [
                InlineKeyboardButton("✅ Ya", callback_data=f"confirm_{action}_{item_id}"),
                InlineKeyboardButton("❌ Tidak", callback_data="cancel"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def transaction_actions(transaction_id: int) -> InlineKeyboardMarkup:
        """Create transaction action keyboard.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            InlineKeyboardMarkup with action options
        """
        keyboard = [
            [
                InlineKeyboardButton("Edit", callback_data=f"edit_trans_{transaction_id}"),
                InlineKeyboardButton("Hapus", callback_data=f"delete_trans_{transaction_id}"),
            ],
            [
                InlineKeyboardButton("Kembali", callback_data="cancel"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def report_period_selection() -> InlineKeyboardMarkup:
        """Create report period selection keyboard.
        
        Returns:
            InlineKeyboardMarkup with period options
        """
        keyboard = [
            [
                InlineKeyboardButton("Hari Ini", callback_data="report_today"),
                InlineKeyboardButton("7 Hari", callback_data="report_7d"),
            ],
            [
                InlineKeyboardButton("30 Hari", callback_data="report_30d"),
                InlineKeyboardButton("Bulan Ini", callback_data="report_this_month"),
            ],
            [
                InlineKeyboardButton("Bulan Lalu", callback_data="report_last_month"),
            ],
            [
                InlineKeyboardButton("❌ Batal", callback_data="cancel"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pagination(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
        """Create pagination keyboard.
        
        Args:
            current_page: Current page number (0-indexed)
            total_pages: Total number of pages
            prefix: Prefix for callback data
            
        Returns:
            InlineKeyboardMarkup with pagination buttons
        """
        keyboard = []
        row = []
        
        if current_page > 0:
            row.append(InlineKeyboardButton("◀ Prev", callback_data=f"{prefix}_page_{current_page-1}"))
        
        row.append(InlineKeyboardButton(f"{current_page+1}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages - 1:
            row.append(InlineKeyboardButton("Next ▶", callback_data=f"{prefix}_page_{current_page+1}"))
        
        keyboard.append(row)
        keyboard.append([InlineKeyboardButton("Kembali", callback_data="cancel")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def budget_actions(budget_id: int) -> InlineKeyboardMarkup:
        """Create budget action keyboard.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            InlineKeyboardMarkup with action options
        """
        keyboard = [
            [
                InlineKeyboardButton("Edit", callback_data=f"edit_budget_{budget_id}"),
                InlineKeyboardButton("Hapus", callback_data=f"delete_budget_{budget_id}"),
            ],
            [
                InlineKeyboardButton("Kembali", callback_data="cancel"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def recurring_actions(recurring_id: int, is_active: bool) -> InlineKeyboardMarkup:
        """Create recurring transaction action keyboard.
        
        Args:
            recurring_id: Recurring transaction ID
            is_active: Whether the recurring transaction is active
            
        Returns:
            InlineKeyboardMarkup with action options
        """
        keyboard = []
        
        if is_active:
            keyboard.append([
                InlineKeyboardButton("Pause", callback_data=f"pause_recurring_{recurring_id}"),
                InlineKeyboardButton("Hapus", callback_data=f"delete_recurring_{recurring_id}"),
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("Resume", callback_data=f"resume_recurring_{recurring_id}"),
                InlineKeyboardButton("Hapus", callback_data=f"delete_recurring_{recurring_id}"),
            ])
        
        keyboard.append([InlineKeyboardButton("Kembali", callback_data="cancel")])
        
        return InlineKeyboardMarkup(keyboard)

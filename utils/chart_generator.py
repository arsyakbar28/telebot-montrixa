"""Chart generation utilities using matplotlib."""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, datetime
from typing import List, Dict, Any
import io
from config.settings import Settings

# Set font to support Unicode characters
plt.rcParams['font.family'] = 'DejaVu Sans'


class ChartGenerator:
    """Utility class for generating charts."""
    
    @staticmethod
    def generate_expense_pie_chart(expense_by_category: List[Dict[str, Any]]) -> io.BytesIO:
        """Generate pie chart for expense breakdown by category.
        
        Args:
            expense_by_category: List of category expense data
            
        Returns:
            BytesIO object containing PNG image
        """
        if not expense_by_category:
            return None
        
        # Prepare data
        labels = [f"{cat['category_name']}" for cat in expense_by_category[:8]]
        sizes = [cat['total_amount'] for cat in expense_by_category[:8]]
        
        # If more than 8 categories, group others
        if len(expense_by_category) > 8:
            others_total = sum(cat['total_amount'] for cat in expense_by_category[8:])
            labels.append('Lainnya')
            sizes.append(others_total)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8), dpi=Settings.CHART_DPI)
        
        # Create pie chart
        colors = plt.cm.Set3(range(len(labels)))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        
        # Style
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_weight('bold')
        
        ax.set_title('Pengeluaran per Kategori', fontsize=14, weight='bold', pad=20)
        
        # Save to BytesIO
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    @staticmethod
    def generate_daily_trend_chart(daily_data: List[Dict[str, Any]]) -> io.BytesIO:
        """Generate line chart for daily income/expense trend.
        
        Args:
            daily_data: List of daily data with date, income, expense
            
        Returns:
            BytesIO object containing PNG image
        """
        if not daily_data:
            return None
        
        # Prepare data
        dates = [data['date'] for data in daily_data]
        income = [data['income'] for data in daily_data]
        expense = [data['expense'] for data in daily_data]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6), dpi=Settings.CHART_DPI)
        
        # Plot lines
        ax.plot(dates, income, marker='o', linewidth=2, label='Pemasukan', color='#2ecc71')
        ax.plot(dates, expense, marker='o', linewidth=2, label='Pengeluaran', color='#e74c3c')
        
        # Fill area
        ax.fill_between(dates, income, alpha=0.3, color='#2ecc71')
        ax.fill_between(dates, expense, alpha=0.3, color='#e74c3c')
        
        # Format x-axis
        if len(dates) > 7:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        plt.xticks(rotation=45)
        
        # Labels and title
        ax.set_xlabel('Tanggal', fontsize=11)
        ax.set_ylabel('Jumlah (Rp)', fontsize=11)
        ax.set_title('Tren Pemasukan & Pengeluaran', fontsize=14, weight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Rp {x:,.0f}'))
        
        # Save to BytesIO
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    @staticmethod
    def generate_bar_chart(data: Dict[str, Any]) -> io.BytesIO:
        """Generate bar chart comparing income and expense.
        
        Args:
            data: Dictionary with income and expense data
            
        Returns:
            BytesIO object containing PNG image
        """
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6), dpi=Settings.CHART_DPI)
        
        categories = ['Pemasukan', 'Pengeluaran']
        values = [data.get('total_income', 0), data.get('total_expense', 0)]
        colors = ['#2ecc71', '#e74c3c']
        
        bars = ax.bar(categories, values, color=colors, width=0.5, alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height,
                f'Rp {height:,.0f}',
                ha='center',
                va='bottom',
                fontsize=11,
                weight='bold'
            )
        
        # Labels and title
        ax.set_ylabel('Jumlah (Rp)', fontsize=11)
        ax.set_title('Perbandingan Pemasukan & Pengeluaran', fontsize=14, weight='bold', pad=20)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Rp {x:,.0f}'))
        ax.grid(True, alpha=0.3, axis='y')
        
        # Save to BytesIO
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    @staticmethod
    def generate_budget_status_chart(budget_status: List[Dict[str, Any]]) -> io.BytesIO:
        """Generate horizontal bar chart for budget status.
        
        Args:
            budget_status: List of budget status data
            
        Returns:
            BytesIO object containing PNG image
        """
        if not budget_status:
            return None
        
        # Prepare data
        categories = [f"{b['category_name']}" for b in budget_status[:10]]
        percentages = [min(b['percentage'], 100) for b in budget_status[:10]]
        
        # Determine colors based on percentage
        colors = []
        for pct in percentages:
            if pct >= 100:
                colors.append('#e74c3c')  # Red
            elif pct >= 90:
                colors.append('#f39c12')  # Orange
            elif pct >= 75:
                colors.append('#f1c40f')  # Yellow
            else:
                colors.append('#2ecc71')  # Green
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, max(6, len(categories) * 0.5)), dpi=Settings.CHART_DPI)
        
        # Create horizontal bar chart
        bars = ax.barh(categories, percentages, color=colors, alpha=0.8)
        
        # Add percentage labels
        for i, (bar, pct) in enumerate(zip(bars, percentages)):
            width = bar.get_width()
            ax.text(
                width + 2,
                bar.get_y() + bar.get_height()/2,
                f'{pct:.1f}%',
                ha='left',
                va='center',
                fontsize=9,
                weight='bold'
            )
        
        # Add 100% reference line
        ax.axvline(x=100, color='gray', linestyle='--', alpha=0.5)
        
        # Labels and title
        ax.set_xlabel('Persentase Terpakai (%)', fontsize=11)
        ax.set_title('Status Penggunaan Budget', fontsize=14, weight='bold', pad=20)
        ax.set_xlim(0, max(110, max(percentages) + 10))
        ax.grid(True, alpha=0.3, axis='x')
        
        # Save to BytesIO
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf

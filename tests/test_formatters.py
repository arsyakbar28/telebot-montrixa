"""Tests for formatter utilities."""

import pytest
from datetime import date, timedelta
from utils.formatters import Formatter


class TestFormatter:
    """Test Formatter class."""
    
    def test_format_currency_idr(self):
        """Test IDR currency formatting."""
        result = Formatter.format_currency(1000000)
        assert result == "Rp 1.000.000"
    
    def test_format_currency_decimal(self):
        """Test currency with decimals."""
        result = Formatter.format_currency(50000.50)
        assert "Rp 50.000" in result
    
    def test_format_date(self):
        """Test date formatting."""
        test_date = date(2024, 2, 13)
        result = Formatter.format_date(test_date)
        assert result == "13/02/2024"
    
    def test_format_date_relative_today(self):
        """Test relative date for today."""
        today = date.today()
        result = Formatter.format_date_relative(today)
        assert result == "Hari ini"
    
    def test_format_date_relative_yesterday(self):
        """Test relative date for yesterday."""
        yesterday = date.today() - timedelta(days=1)
        result = Formatter.format_date_relative(yesterday)
        assert result == "Kemarin"
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        result = Formatter.format_percentage(75.5)
        assert result == "75.5%"
    
    def test_format_percentage_no_decimal(self):
        """Test percentage formatting without decimals."""
        result = Formatter.format_percentage(100, decimals=0)
        assert result == "100%"
    
    def test_format_period_daily(self):
        """Test daily period formatting."""
        result = Formatter.format_period("daily")
        assert result == "Harian"
    
    def test_format_period_weekly(self):
        """Test weekly period formatting."""
        result = Formatter.format_period("weekly")
        assert result == "Mingguan"
    
    def test_format_period_monthly(self):
        """Test monthly period formatting."""
        result = Formatter.format_period("monthly")
        assert result == "Bulanan"

"""Tests for validator utilities."""

import pytest
from utils.validators import Validator


class TestValidator:
    """Test Validator class."""
    
    def test_validate_amount_valid(self):
        """Test valid amount validation."""
        is_valid, amount, error = Validator.validate_amount("50000")
        assert is_valid is True
        assert amount == 50000
        assert error is None
    
    def test_validate_amount_with_separator(self):
        """Test amount with separator."""
        is_valid, amount, error = Validator.validate_amount("1.000.000")
        assert is_valid is True
        assert amount == 1000000
    
    def test_validate_amount_negative(self):
        """Test negative amount."""
        is_valid, amount, error = Validator.validate_amount("-100")
        assert is_valid is False
        assert "lebih besar dari 0" in error
    
    def test_validate_amount_zero(self):
        """Test zero amount."""
        is_valid, amount, error = Validator.validate_amount("0")
        assert is_valid is False
    
    def test_validate_amount_invalid(self):
        """Test invalid amount."""
        is_valid, amount, error = Validator.validate_amount("abc")
        assert is_valid is False
        assert "tidak valid" in error
    
    def test_validate_period_daily(self):
        """Test daily period."""
        is_valid, period, error = Validator.validate_period("harian")
        assert is_valid is True
        assert period == "daily"
    
    def test_validate_period_weekly(self):
        """Test weekly period."""
        is_valid, period, error = Validator.validate_period("mingguan")
        assert is_valid is True
        assert period == "weekly"
    
    def test_validate_period_monthly(self):
        """Test monthly period."""
        is_valid, period, error = Validator.validate_period("bulanan")
        assert is_valid is True
        assert period == "monthly"
    
    def test_validate_period_invalid(self):
        """Test invalid period."""
        is_valid, period, error = Validator.validate_period("invalid")
        assert is_valid is False
    
    def test_validate_transaction_type_income(self):
        """Test income type."""
        is_valid, trans_type, error = Validator.validate_transaction_type("pemasukan")
        assert is_valid is True
        assert trans_type == "income"
    
    def test_validate_transaction_type_expense(self):
        """Test expense type."""
        is_valid, trans_type, error = Validator.validate_transaction_type("pengeluaran")
        assert is_valid is True
        assert trans_type == "expense"
    
    def test_validate_description_valid(self):
        """Test valid description."""
        is_valid, desc, error = Validator.validate_description("Makan siang")
        assert is_valid is True
        assert desc == "Makan siang"
    
    def test_validate_description_empty(self):
        """Test empty description."""
        is_valid, desc, error = Validator.validate_description("")
        assert is_valid is False
        assert "tidak boleh kosong" in error
    
    def test_validate_description_too_long(self):
        """Test too long description."""
        long_desc = "a" * 501
        is_valid, desc, error = Validator.validate_description(long_desc)
        assert is_valid is False
        assert "terlalu panjang" in error

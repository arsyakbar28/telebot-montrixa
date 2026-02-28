"""Input validation utilities."""

from typing import Optional, Tuple
import re


class Validator:
    """Utility class for input validation."""
    
    @staticmethod
    def validate_amount(amount_str: str) -> Tuple[bool, Optional[float], Optional[str]]:
        """Validate and parse amount string.
        
        Args:
            amount_str: Amount string to validate
            
        Returns:
            Tuple of (is_valid, parsed_amount, error_message)
        """
        # Remove common separators
        amount_str = amount_str.replace('.', '').replace(',', '').strip()
        
        try:
            amount = float(amount_str)
            
            if amount <= 0:
                return False, None, "Jumlah harus lebih besar dari 0"
            
            if amount > 999999999999:
                return False, None, "Jumlah terlalu besar"
            
            return True, amount, None
        except ValueError:
            return False, None, "Format jumlah tidak valid. Gunakan angka saja."
    
    @staticmethod
    def validate_period(period: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate budget period.
        
        Args:
            period: Period string
            
        Returns:
            Tuple of (is_valid, normalized_period, error_message)
        """
        period = period.lower().strip()
        
        period_map = {
            'daily': 'daily',
            'harian': 'daily',
            'day': 'daily',
            'hari': 'daily',
            'weekly': 'weekly',
            'mingguan': 'weekly',
            'week': 'weekly',
            'minggu': 'weekly',
            'monthly': 'monthly',
            'bulanan': 'monthly',
            'month': 'monthly',
            'bulan': 'monthly',
        }
        
        normalized = period_map.get(period)
        if normalized:
            return True, normalized, None
        else:
            return False, None, "Period harus: harian/mingguan/bulanan"
    
    @staticmethod
    def validate_frequency(frequency: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate recurring frequency.
        
        Args:
            frequency: Frequency string
            
        Returns:
            Tuple of (is_valid, normalized_frequency, error_message)
        """
        # Same as period validation
        return Validator.validate_period(frequency)
    
    @staticmethod
    def validate_transaction_type(trans_type: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate transaction type.
        
        Args:
            trans_type: Transaction type string
            
        Returns:
            Tuple of (is_valid, normalized_type, error_message)
        """
        trans_type = trans_type.lower().strip()
        
        type_map = {
            'income': 'income',
            'pemasukan': 'income',
            'masuk': 'income',
            'in': 'income',
            'expense': 'expense',
            'pengeluaran': 'expense',
            'keluar': 'expense',
            'out': 'expense',
        }
        
        normalized = type_map.get(trans_type)
        if normalized:
            return True, normalized, None
        else:
            return False, None, "Tipe harus: pemasukan/pengeluaran"
    
    @staticmethod
    def parse_command_args(text: str, expected_count: Optional[int] = None) -> list:
        """Parse command arguments from text.
        
        Args:
            text: Command text
            expected_count: Expected number of arguments
            
        Returns:
            List of arguments
        """
        # Remove command from text
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            return []
        
        # Split remaining text
        args_text = parts[1]
        
        # Simple split by whitespace
        args = args_text.split()
        
        # If expected count is specified, try to merge extra args
        if expected_count and len(args) > expected_count:
            # Merge remaining args into the last one
            merged = args[:expected_count-1]
            merged.append(' '.join(args[expected_count-1:]))
            return merged
        
        return args
    
    @staticmethod
    def validate_description(description: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate transaction description.
        
        Args:
            description: Description string
            
        Returns:
            Tuple of (is_valid, cleaned_description, error_message)
        """
        description = description.strip()
        
        if not description:
            return False, None, "Deskripsi tidak boleh kosong"
        
        if len(description) > 500:
            return False, None, "Deskripsi terlalu panjang (max 500 karakter)"
        
        return True, description, None
    
    @staticmethod
    def validate_category_name(name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate category name.
        
        Args:
            name: Category name
            
        Returns:
            Tuple of (is_valid, cleaned_name, error_message)
        """
        name = name.strip()
        
        if not name:
            return False, None, "Nama kategori tidak boleh kosong"
        
        if len(name) > 100:
            return False, None, "Nama kategori terlalu panjang (max 100 karakter)"
        
        return True, name, None

"""Script to add Langganan category to all existing users."""

import sys
sys.path.append('.')

from models.user import User
from models.category import Category

def add_langganan_category():
    """Add Langganan category to all existing users."""
    
    # Get all active users
    users = User.get_all_active()
    
    print(f"Found {len(users)} active users")
    
    count = 0
    for user in users:
        # Check if user already has Langganan category
        existing = Category.get_by_name(user.id, 'Langganan', 'expense')
        
        if existing:
            print(f"User {user.telegram_id} already has Langganan category, skipping...")
            continue
        
        # Create Langganan category
        category = Category.create(
            user_id=user.id,
            name='Langganan',
            cat_type='expense',
            icon='📱',
            is_default=True
        )
        
        if category:
            print(f"✅ Added Langganan category to user {user.telegram_id}")
            count += 1
        else:
            print(f"❌ Failed to add Langganan category to user {user.telegram_id}")
    
    print(f"\n✅ Successfully added Langganan category to {count} users")

if __name__ == '__main__':
    print("=" * 60)
    print("Adding Langganan Category to Existing Users")
    print("=" * 60)
    add_langganan_category()

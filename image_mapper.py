#!/usr/bin/env python3
"""
Utility to help map existing menu images to database items
"""

import os
from database import MenuDatabase

def list_menu_images():
    """List all available menu images"""
    image_dir = "static/images/taj_nikko_fuji_menu_images"
    if not os.path.exists(image_dir):
        print(f"Directory {image_dir} not found!")
        return []
    
    images = []
    for filename in sorted(os.listdir(image_dir)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.avif')):
            images.append(filename)
    
    return images

def suggest_image_mappings():
    """Suggest image mappings based on filename patterns"""
    db = MenuDatabase()
    items_without_images = db.get_items_without_images()
    available_images = list_menu_images()
    
    print("=== MENU IMAGE MAPPING SUGGESTIONS ===\n")
    
    # Create mapping suggestions
    suggestions = []
    
    # Common mappings based on your image filenames
    image_mappings = {
        # Salads & Tandoori
        "0 Salad Tandoori 1.png": ["Caesar Salad", "Taj Green Salad"],
        "0 Salad Tandoori 2.png": ["Mini Salad", "Seekh Kabab"],
        "0 Salad Tandoori 3.png": ["Tandoori Chicken", "Chicken Tikka"],
        
        # Snacks
        "1 Snacks 1.png": ["Samosa", "Papad"],
        "1 Snacks 2.png": ["Vegetable Pakoda", "Fried Potato"],
        "1 Snacks 3.png": ["Fried Chicken (Karaage)", "Wing Fry"],
        "1 Snacks 4.png": ["Prawn Crackers", "Prawn Aurora Sauce"],
        "1 Snacks 5.png": ["Shrimp Toast", "Chicken with Eggplant"],
        
        # Set Menu
        "2 Set Menu 1.png": ["Double Curry Set"],
        "2 Set Menu 2.png": ["Vegetarian Set"],
        "2 Set Menu 3.png": ["Tandoori Set"],
        "2 Set Menu 4.png": ["Kids Set"],
        
        # Curries
        "3 Curry 1.png": ["Chicken Butter Masala", "Chicken Curry"],
        "3 Curry 2.png": ["Coconut Chicken Curry", "Chicken Kashmiri"],
        "3 Curry 3.png": ["Chicken Do Piaza", "Sag Chicken"],
        "3 Curry 4.png": ["Chicken Tikka Masala", "Mutton Curry"],
        "3 Curry 5.png": ["Sag Mutton", "Keema Curry"],
        "3 Curry 6.png": ["Prawn Masala", "Vegetable Curry"],
        "3 Curry 7.png": ["Palak Paneer", "Sahi Paneer"],
        "3 Curry 8.png": ["Chana Masala", "Pulao"],
        
        # Nan & Rice
        "4 Nan & Rice 1.png": ["Nan", "Garlic Nan"],
        "4 Nan & Rice 2.png": ["Garlic Cheese Nan", "Cheese Nan"],
        "4 Nan & Rice 3.png": ["Kabuli Nan", "Rice"],
        "4 Nan & Rice 4.png": ["Cumin Rice (Basmati)", "Salad Set"],
        "4 Nan & Rice 5.png": ["Chicken Biryani", "Mutton Biryani"],
        
        # Fusion & Dessert
        "6 Fusion & Dessert1.png": ["Pad Thai"],
        "6 Fusion & Dessert2.png": ["Gappao Rice"],
        "6 Fusion & Dessert3.png": ["Tomato Pizza with Basil Sauce"],
        "6 Fusion & Dessert4.png": ["Margrita"],
        "6 Fusion & Dessert5.png": ["Chicken Pizza"],
        "6 Fusion & Dessert6.png": ["Mango Kulfi"],
        "6 Fusion & Dessert7.png": ["Kheer"],
        "6 Fusion & Dessert8.png": ["Vanilla ice cream", "Rasgula"],
    }
    
    print("Available Images:")
    for i, img in enumerate(available_images, 1):
        print(f"{i:2d}. {img}")
    
    print(f"\nMenu Items Without Images ({len(items_without_images)}):")
    for i, item in enumerate(items_without_images, 1):
        print(f"{i:2d}. {item['name_en']} ({item['category_name']})")
    
    print("\n" + "="*60)
    print("SUGGESTED MAPPINGS:")
    print("="*60)
    
    for image_file, suggested_items in image_mappings.items():
        if image_file in available_images:
            print(f"\n📸 {image_file}")
            for item_name in suggested_items:
                # Find matching item
                matching_item = None
                for item in items_without_images:
                    if item['name_en'] == item_name:
                        matching_item = item
                        break
                
                if matching_item:
                    image_url = f"/static/images/taj_nikko_fuji_menu_images/{image_file}"
                    print(f"   → {item_name} (ID: {matching_item['id']})")
                    print(f"     URL: {image_url}")
                else:
                    print(f"   → {item_name} (not found in database)")
    
    print("\n" + "="*60)
    print("COPY-PASTE READY COMMANDS:")
    print("="*60)
    print("# You can copy these URLs to the admin interface at http://localhost:5000/admin/menu")
    print()
    
    for image_file, suggested_items in image_mappings.items():
        if image_file in available_images:
            image_url = f"http://localhost:5000/static/images/taj_nikko_fuji_menu_images/{image_file}"
            print(f"# For {image_file}:")
            for item_name in suggested_items:
                matching_item = None
                for item in items_without_images:
                    if item['name_en'] == item_name:
                        matching_item = item
                        break
                if matching_item:
                    print(f"# {item_name}: {image_url}")
            print()

def main():
    """Main function"""
    suggest_image_mappings()

if __name__ == "__main__":
    main()

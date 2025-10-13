#!/usr/bin/env python3
"""
Database setup and management for Taj Restaurant Menu System
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple

class MenuDatabase:
    def __init__(self, db_path: str = "taj_menu.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_en TEXT NOT NULL,
                    name_jp TEXT NOT NULL,
                    icon TEXT,
                    sort_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create menu_items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    name_en TEXT NOT NULL,
                    name_jp TEXT NOT NULL,
                    description_en TEXT,
                    description_jp TEXT,
                    price INTEGER NOT NULL,
                    price_2p INTEGER,
                    price_4p INTEGER,
                    image_url TEXT,
                    image_alt TEXT,
                    is_available BOOLEAN DEFAULT 1,
                    is_spicy BOOLEAN DEFAULT 0,
                    spice_levels TEXT, -- JSON array of available spice levels
                    allergens TEXT, -- JSON array of allergens
                    dietary_tags TEXT, -- JSON array (vegetarian, vegan, halal, etc.)
                    sort_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            ''')
            
            # Create restaurant_menu table (for location-specific menus)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS restaurant_menus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    restaurant_location TEXT NOT NULL, -- 'okinawa', 'nikko', 'fuji'
                    menu_item_id INTEGER NOT NULL,
                    is_featured BOOLEAN DEFAULT 0,
                    location_price INTEGER, -- Override price for specific location
                    location_availability BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id),
                    UNIQUE(restaurant_location, menu_item_id)
                )
            ''')
            
            # Create menu_sets table (for combo meals)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu_sets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_en TEXT NOT NULL,
                    name_jp TEXT NOT NULL,
                    description_en TEXT,
                    description_jp TEXT,
                    price INTEGER NOT NULL,
                    image_url TEXT,
                    restaurant_location TEXT NOT NULL DEFAULT 'all',
                    is_available BOOLEAN DEFAULT 1,
                    sort_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create set_items table (items included in sets)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS set_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    set_id INTEGER NOT NULL,
                    menu_item_id INTEGER,
                    item_description_en TEXT, -- For custom items not in menu_items
                    item_description_jp TEXT,
                    quantity INTEGER DEFAULT 1,
                    is_choice BOOLEAN DEFAULT 0, -- If customer can choose from options
                    FOREIGN KEY (set_id) REFERENCES menu_sets(id),
                    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
                )
            ''')
            
            # Create orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT UNIQUE NOT NULL,
                    customer_info TEXT,
                    items TEXT NOT NULL,
                    total_amount INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    restaurant_location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    qr_code_path TEXT
                )
            ''')
            
            conn.commit()

    def insert_sample_data(self):
        """Insert sample data from the menu images."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert categories
            categories = [
                ("Salad", "サラダ", "fas fa-seedling", 1),
                ("Tandoori", "タンドリー", "fas fa-fire", 2),
                ("Snacks", "スナック", "fas fa-utensils", 3),
                ("Curry Set", "カレーセット", "fas fa-utensils", 4),
                ("Chicken Curry", "チキンカレー", "fas fa-bowl-rice", 5),
                ("Other Curries", "その他のカレー", "fas fa-bowl-rice", 6),
                ("Nan & Rice", "ナン & ライス", "fas fa-bread-slice", 7),
                ("Fusion Cuisine", "フュージョンクイジーン", "fas fa-utensils", 8),
                ("Pizza", "ピザ", "fas fa-pizza-slice", 9),
                ("Dessert", "デザート", "fas fa-ice-cream", 10)
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO categories (name_en, name_jp, icon, sort_order)
                VALUES (?, ?, ?, ?)
            ''', categories)
            
            # Get category IDs
            category_map = {}
            cursor.execute("SELECT id, name_en FROM categories")
            for cat_id, cat_name in cursor.fetchall():
                category_map[cat_name] = cat_id
            
            # Insert menu items
            menu_items = [
                # Salads
                (category_map["Salad"], "Caesar Salad", "シーザーサラダ", 
                 "Lettuce-based salad topped with Parmesan cheese and croutons",
                 "パルメザンチーズやクルトンをトッピングした、レタス等の葉菜中心のサラダ",
                 750, None, None, None, None, 1, 0),
                
                (category_map["Salad"], "Taj Green Salad", "タージグリーンサラダ",
                 "Fresh seasonal green vegetables arranged with spices (2-3 person green salad)",
                 "季節の新鮮な緑野菜をスパイシに盛り付けたヘルシーなサリサラダ（2〜3人前のグリーンサラダ）",
                 750, None, None, None, None, 1, 0),
                
                (category_map["Salad"], "Mini Salad", "ミニサラダ",
                 "Mini green salad (1 person green salad)",
                 "ミニグリーンサラダです（1人前のグリーンサラダ）",
                 400, None, None, None, None, 1, 0),
                
                # Tandoori
                (category_map["Tandoori"], "Seekh Kabab", "シークカバブ",
                 "Ground meat mixed with spices, wrapped around iron skewer and grilled",
                 "ひき肉にスパイスを練り込み、鉄串に巻きつけて焼きました",
                 650, 650, 1200, None, None, 1, 1),
                
                (category_map["Tandoori"], "Tandoori Chicken", "タンドリーチキン",
                 "Bone-in chicken leg deep-steamed with Indian spices",
                 "骨付きチキンレッグのインドのスパイスで深蒸し",
                 650, 650, 1200, None, None, 1, 1),
                
                (category_map["Tandoori"], "Chicken Tikka", "チキンティッカ",
                 "Boneless barbecue chicken",
                 "骨なしのバーベキューチキン",
                 500, 500, 950, None, None, 1, 1),
                
                (category_map["Tandoori"], "Lamb Chop", "ラムチョップ",
                 "Bone-in lamb meat marinated in mild spices",
                 "少し羊のスパイスに漬けた骨付きラム肉",
                 850, 850, None, None, None, 1, 1),
                
                (category_map["Tandoori"], "Tandoori Prawn", "タンドリープラウン",
                 "Grilled with various spice seasonings",
                 "数種きなこのふりふりに焼きました",
                 600, 600, None, None, None, 1, 1),
                
                (category_map["Tandoori"], "Tandoori Mix Grill", "タンドリーミックスグリル",
                 "2 pieces each of Seekh Kabab, Tandoori Chicken, Chicken Tikka, Tandoori Prawn, Lamb Chop",
                 "シークカバブ、タンドリーチキン、チキンティッカ、タンドリープラウン、ラムチョップを2ピース",
                 3500, None, None, None, None, 1, 1),
                
                (category_map["Tandoori"], "Chicken Tangri Kabab", "チキンタングリーカバブ",
                 None, None, 650, None, None, None, None, 1, 1),
                
                # Snacks
                (category_map["Snacks"], "Samosa", "サモサ",
                 "Deep-fried pastry filled with spiced potatoes and green peas",
                 "グリーンピースやカレー風味に味付けしたじゃがいもを包んだ皮で揚げた料理",
                 750, 750, None, None, None, 1, 0),
                
                (category_map["Snacks"], "Papad", "パパド",
                 "Thin crispy wafer made from lentil flour, similar to crackers",
                 "豆粉をこねて薄くのばし焼いた、せんべいに似たおつまみ",
                 450, None, None, None, None, 1, 0),
                
                (category_map["Snacks"], "Vegetable Pakoda", "ベジタブルパコラ",
                 "Mixed vegetables in Indian-style tempura batter",
                 "色んな野菜をばってインド風天ぷら料理のかき揚げ",
                 850, None, None, None, None, 1, 0),
                
                # Chicken Curries
                (category_map["Chicken Curry"], "Chicken Butter Masala", "チキンバターマサラ",
                 "Rich and creamy chicken curry made with butter and milk",
                 "バターを使って濃厚な味わいに仕上げた牛乳のチキンカレー",
                 1300, None, None, None, None, 1, 1),
                
                (category_map["Chicken Curry"], "Chicken Curry", "チキンカレー",
                 "Classic curry made with simmered chicken",
                 "鶏肉を煮込んで作った定番のカレー",
                 1250, None, None, None, None, 1, 1),
                
                (category_map["Chicken Curry"], "Coconut Chicken Curry", "ココナッツチキンカレー",
                 "Chicken curry with rich coconut base and sweet coconut flavor",
                 "深みのあるココナッツ甘さと内容のココナッツベースのチキンカレー",
                 1250, None, None, None, None, 1, 1),
                
                # Other Curries
                (category_map["Other Curries"], "Mutton Curry", "マトンカレー",
                 "Made with tender lamb meat, perfectly paired with spices",
                 "柔らかいラム肉を使用、スパイスとの相性は抜群です",
                 1300, None, None, None, None, 1, 1),
                
                (category_map["Other Curries"], "Keema Curry", "キーマカレー",
                 "Rich curry made with ground meat",
                 "挽き肉を使った濃厚なカレー",
                 1150, None, None, None, None, 1, 1),
                
                (category_map["Other Curries"], "Vegetable Curry", "ベジタブルカレー",
                 "Healthy curry made with seasonal vegetables",
                 "季節の野菜を使ったヘルシーなカレー",
                 1150, None, None, None, None, 1, 1),
                
                # Nan & Rice
                (category_map["Nan & Rice"], "Nan", "ナン",
                 "Fluffy and chewy bread representing India",
                 "ふわふわもちもちのインド代表するパン",
                 350, None, None, None, None, 1, 0),
                
                (category_map["Nan & Rice"], "Garlic Nan", "ガーリックナン",
                 "Aromatic nan topped with finely chopped garlic",
                 "細かく刻んだガーリックをトッピングした、香りの良いナン",
                 650, None, None, None, None, 1, 0),
                
                (category_map["Nan & Rice"], "Cheese Nan", "チーズナン",
                 "Popular nan made with mozzarella cheese kneaded into the dough",
                 "生地にモッツァレラチーズを練んで焼き上げた大人気のナン",
                 650, None, None, None, None, 1, 0),
                
                (category_map["Nan & Rice"], "Rice", "ライス",
                 "Light and slightly firm rice that pairs well with curry",
                 "カレーによく合うさっぱりと少し固めに炊き上げています",
                 500, None, None, None, None, 1, 0),
                
                (category_map["Nan & Rice"], "Chicken Biryani", "チキンビリヤニ",
                 "Indian-style mixed rice with chicken",
                 "鶏肉を使ったインド風の炊き込みご飯",
                 1600, None, None, None, None, 1, 1),
                
                # Fusion Cuisine
                (category_map["Fusion Cuisine"], "Pad Thai", "パッタイ",
                 "Thai-style fried noodles with rice noodles",
                 "ライスヌードルを使ったタイ風の焼きそば",
                 1100, None, None, None, None, 1, 0),
                
                (category_map["Fusion Cuisine"], "Gappao Rice", "ガパオライス",
                 "Thai dish with stir-fried chicken, holy basil, fried egg and oyster sauce",
                 "鶏肉炒めやホーリーバジルなどをタマゴフライ、オイスターソースとともに炒めたタイ料理",
                 1100, None, None, None, None, 1, 0),
                
                # Pizza
                (category_map["Pizza"], "Tomato Pizza with Basil Sauce", "トマトピザバジルソース",
                 "Pizza with tomato and basil sauce",
                 "トマトとバジルソースを使ったピザ",
                 1600, None, None, None, None, 1, 0),
                
                (category_map["Pizza"], "Margrita", "マルゲリータ",
                 "Simple pizza with mozzarella cheese and tomato",
                 "モッツァレラチーズとトマトのシンプルなピザ",
                 1600, None, None, None, None, 1, 0),
                
                (category_map["Pizza"], "Chicken Pizza", "チキンピザ",
                 "Pizza with chicken",
                 "鶏肉を使ったピザ",
                 1600, None, None, None, None, 1, 0),
                
                # Desserts
                (category_map["Dessert"], "Mango Kulfi", "マンゴクルフィ",
                 "Indian mango flavored ice cream",
                 "インドのマンゴ味アイスクリーム",
                 550, None, None, None, None, 1, 0),
                
                (category_map["Dessert"], "Kheer", "キール",
                 "Indian rice pudding",
                 "インドのライスプディング",
                 550, None, None, None, None, 1, 0),
                
                (category_map["Dessert"], "Vanilla ice cream", "バニラアイス",
                 None, None, 550, None, None, None, None, 1, 0),
                
                (category_map["Dessert"], "Rasgula", "ラスグラ",
                 "Representative Indian sweet dessert",
                 "インドの代表的な甘いデザート",
                 550, None, None, None, None, 1, 0)
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO menu_items 
                (category_id, name_en, name_jp, description_en, description_jp, price, price_2p, price_4p, 
                 image_url, image_alt, is_available, is_spicy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', menu_items)
            
            # Insert restaurant-specific menu items (Nikko & Fuji)
            cursor.execute("SELECT id FROM menu_items")
            menu_item_ids = [row[0] for row in cursor.fetchall()]
            
            restaurant_menus = []
            for location in ['nikko', 'fuji']:
                for item_id in menu_item_ids:
                    restaurant_menus.append((location, item_id, 0, None, 1))
            
            cursor.executemany('''
                INSERT OR IGNORE INTO restaurant_menus 
                (restaurant_location, menu_item_id, is_featured, location_price, location_availability)
                VALUES (?, ?, ?, ?, ?)
            ''', restaurant_menus)
            
            # Insert set menus
            set_menus = [
                ("Double Curry Set", "ダブルカレーセット",
                 "2 Choice Curry, Nan, Rice, Salad, Softdrink, Dessert",
                 "選べる2種類のカレー、ナン、ライス、サラダ、ソフトドリンク、デザート",
                 1850, None, "nikko", 1, 1),
                
                ("Vegetarian Set", "ベジタリアンセット",
                 "3 Vegetable Curry, Nan, Mini Rice, Salad, Papad, Softdrink, Dessert",
                 "3種類のベジタブルカレー、ナン、ミニライス、サラダ、パパド、ソフトドリンク、デザート",
                 1850, None, "nikko", 1, 2),
                
                ("Tandoori Set", "タンドリーセット",
                 "1 Choice Curry, Nan, Mini Rice, Tandoori Chicken 1P, Seekh Kabab 1P, Chicken Tikka 1P, Salad, Softdrink",
                 "選べる1種類のカレー、ナン、ミニライス、タンドリーチキン1P、シークカバブ1P、チキンティッカ1P、サラダ、ソフトドリンク",
                 2050, None, "nikko", 1, 3),
                
                ("Kids Set", "お子様セット",
                 "Butter Chicken - Mini Nan Mini Rice Salad, Dessert Orange Juice or Lassie",
                 "甘口バターチキン、ミニナン、ミニライス、フルーツライス、オレンジジュースまたはラッシー",
                 1000, None, "all", 1, 4),
                
                # Okinawa specific sets
                ("Okinawa Curry Set", "沖縄カレーセット",
                 "2 Choice Curry, Nan, Rice, Salad, Softdrink, Dessert",
                 "選べる2種類のカレー、ナン、ライス、サラダ、ソフトドリンク、デザート",
                 1950, None, "okinawa", 1, 5),
                
                ("Okinawa Tandoori Set", "沖縄タンドリーセット",
                 "1 Choice Curry, Nan, Mini Rice, Tandoori Chicken 1P, Seekh Kabab 1P, Chicken Tikka 1P, Salad, Softdrink",
                 "選べる1種類のカレー、ナン、ミニライス、タンドリーチキン1P、シークカバブ1P、チキンティッカ1P、サラダ、ソフトドリンク",
                 2150, None, "okinawa", 1, 6)
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO menu_sets 
                (name_en, name_jp, description_en, description_jp, price, image_url, restaurant_location, is_available, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', set_menus)
            
            conn.commit()

    def get_menu_by_location(self, location: str) -> Dict:
        """Get complete menu for a specific restaurant location."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get categories with items
            cursor.execute('''
                SELECT DISTINCT c.id, c.name_en, c.name_jp, c.icon, c.sort_order
                FROM categories c
                JOIN menu_items mi ON c.id = mi.category_id
                JOIN restaurant_menus rm ON mi.id = rm.menu_item_id
                WHERE rm.restaurant_location = ? AND rm.location_availability = 1
                ORDER BY c.sort_order
            ''', (location,))
            
            categories = []
            for cat_row in cursor.fetchall():
                category = dict(cat_row)
                
                # Get items for this category
                cursor.execute('''
                    SELECT mi.*, rm.location_price, rm.is_featured
                    FROM menu_items mi
                    JOIN restaurant_menus rm ON mi.id = rm.menu_item_id
                    WHERE mi.category_id = ? AND rm.restaurant_location = ? AND rm.location_availability = 1
                    ORDER BY mi.sort_order, mi.name_en
                ''', (category['id'], location))
                
                items = []
                for item_row in cursor.fetchall():
                    item = dict(item_row)
                    # Use location price if available, otherwise use default price
                    if item['location_price']:
                        item['display_price'] = item['location_price']
                    else:
                        item['display_price'] = item['price']
                    items.append(item)
                
                category['items'] = items
                categories.append(category)
            
            # Get set menus for this location
            # Logic: 
            # - 'all' sets show everywhere
            # - 'nikko' and 'fuji' sets show in both nikko and fuji (but not okinawa)
            # - 'okinawa' sets show only in okinawa
            if location == 'okinawa':
                cursor.execute('''
                    SELECT * FROM menu_sets 
                    WHERE is_available = 1 
                    AND (restaurant_location = 'all' OR restaurant_location = 'okinawa')
                    ORDER BY sort_order
                ''')
            else:  # nikko or fuji
                cursor.execute('''
                    SELECT * FROM menu_sets 
                    WHERE is_available = 1 
                    AND (restaurant_location = 'all' OR restaurant_location = 'nikko' OR restaurant_location = 'fuji')
                    ORDER BY sort_order
                ''')
            
            sets = [dict(row) for row in cursor.fetchall()]
            
            return {
                'categories': categories,
                'sets': sets
            }

    def add_menu_item(self, category_id: int, name_en: str, name_jp: str, 
                      price: int, description_en: str = None, description_jp: str = None,
                      image_url: str = None, **kwargs) -> int:
        """Add a new menu item."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO menu_items 
                (category_id, name_en, name_jp, description_en, description_jp, price, image_url,
                 price_2p, price_4p, is_spicy, allergens, dietary_tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (category_id, name_en, name_jp, description_en, description_jp, price, image_url,
                  kwargs.get('price_2p'), kwargs.get('price_4p'), kwargs.get('is_spicy', 0),
                  kwargs.get('allergens'), kwargs.get('dietary_tags')))
            
            item_id = cursor.lastrowid
            conn.commit()
            return item_id

    def update_menu_item_image(self, item_id: int, image_url: str, image_alt: str = None):
        """Update menu item image."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE menu_items 
                SET image_url = ?, image_alt = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (image_url, image_alt, item_id))
            
            conn.commit()
    
    def create_order(self, order_data: Dict) -> str:
        """Create a new order and return the order number."""
        import json
        import uuid
        from datetime import datetime
        
        # Generate unique order number
        order_number = f"TAJ-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (
                    order_number, customer_info, items, total_amount, 
                    restaurant_location, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                order_number,
                json.dumps(order_data.get('customer_info', {})),
                json.dumps(order_data['items']),
                order_data['total_amount'],
                order_data.get('restaurant_location', ''),
                'new'
            ))
            conn.commit()
        
        return order_number
    
    def get_order(self, order_number: str) -> Optional[Dict]:
        """Get order details by order number."""
        import json
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))
            row = cursor.fetchone()
            
            if row:
                order = dict(row)
                order['items'] = json.loads(order['items'])
                order['customer_info'] = json.loads(order['customer_info']) if order['customer_info'] else {}
                return order
            return None
    
    def get_pending_orders(self) -> List[Dict]:
        """Get all pending orders."""
        return self.get_orders_by_status('pending')
    
    def get_pending_orders_by_location(self, restaurant_location: str) -> List[Dict]:
        """Get all pending orders for a specific restaurant location."""
        return self.get_orders_by_status_and_location('pending', restaurant_location)
    
    def get_orders_by_status(self, status: str) -> List[Dict]:
        """Get all orders by status."""
        import json
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM orders 
                WHERE status = ? 
                ORDER BY created_at DESC
            ''', (status,))
            
            orders = []
            for row in cursor.fetchall():
                order = dict(row)
                order['items'] = json.loads(order['items'])
                order['customer_info'] = json.loads(order['customer_info']) if order['customer_info'] else {}
                orders.append(order)
            
            return orders
    
    def get_orders_by_status_and_location(self, status: str, restaurant_location: str) -> List[Dict]:
        """Get all orders by status and restaurant location."""
        import json
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM orders 
                WHERE status = ? AND restaurant_location = ?
                ORDER BY created_at DESC
            ''', (status, restaurant_location))
            
            orders = []
            for row in cursor.fetchall():
                order = dict(row)
                order['items'] = json.loads(order['items'])
                order['customer_info'] = json.loads(order['customer_info']) if order['customer_info'] else {}
                orders.append(order)
            
            return orders
    
    def update_order_status(self, order_number: str, status: str):
        """Update order status."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if status == 'completed':
                cursor.execute('''
                    UPDATE orders 
                    SET status = ?, completed_at = CURRENT_TIMESTAMP
                    WHERE order_number = ?
                ''', (status, order_number))
            else:
                cursor.execute('''
                    UPDATE orders 
                    SET status = ?
                    WHERE order_number = ?
                ''', (status, order_number))
            
            conn.commit()
    
    def update_order_qr_path(self, order_number: str, qr_path: str):
        """Update QR code path for an order."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE orders 
                SET qr_code_path = ?
                WHERE order_number = ?
            ''', (qr_path, order_number))
            conn.commit()

    def get_items_without_images(self) -> List[Dict]:
        """Get all menu items that don't have images yet."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT mi.id, mi.name_en, mi.name_jp, c.name_en as category_name
                FROM menu_items mi
                JOIN categories c ON mi.category_id = c.id
                WHERE mi.image_url IS NULL OR mi.image_url = ''
                ORDER BY c.sort_order, mi.name_en
            ''')
            
            return [dict(row) for row in cursor.fetchall()]

    def get_all_set_menus(self) -> List[Dict]:
        """Get all set menus for admin interface."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM menu_sets 
                ORDER BY sort_order, name_en
            ''')
            
            return [dict(row) for row in cursor.fetchall()]

    def update_set_menu_restaurant_location(self, set_id: int, restaurant_location: str):
        """Update restaurant location for a set menu."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE menu_sets 
                SET restaurant_location = ?
                WHERE id = ?
            ''', (restaurant_location, set_id))
            
            conn.commit()

    def get_english_name_for_item(self, item_id: int, item_type: str = 'menu_item') -> str:
        """Get English name for a menu item or set menu by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if item_type == 'set_menu':
                cursor.execute('SELECT name_en FROM menu_sets WHERE id = ?', (item_id,))
            else:
                cursor.execute('SELECT name_en FROM menu_items WHERE id = ?', (item_id,))
            
            result = cursor.fetchone()
            return result[0] if result else None

    def add_set_menu(self, name_en: str, name_jp: str, description_en: str = None, 
                    description_jp: str = None, price: int = 0, image_url: str = None,
                    restaurant_location: str = 'all', is_available: bool = True, 
                    sort_order: int = 0) -> int:
        """Add a new set menu."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO menu_sets 
                (name_en, name_jp, description_en, description_jp, price, image_url, 
                 restaurant_location, is_available, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name_en, name_jp, description_en, description_jp, price, image_url,
                  restaurant_location, is_available, sort_order))
            
            set_id = cursor.lastrowid
            conn.commit()
            return set_id


def main():
    """Initialize database and insert sample data."""
    print("Initializing Taj Restaurant Menu Database...")
    
    db = MenuDatabase()
    
    print("Inserting sample menu data...")
    db.insert_sample_data()
    
    print("Database setup complete!")
    
    # Test the database
    print("\nTesting database - Nikko menu:")
    nikko_menu = db.get_menu_by_location('nikko')
    print(f"Found {len(nikko_menu['categories'])} categories")
    print(f"Found {len(nikko_menu['sets'])} set menus")
    
    # Show items without images
    items_without_images = db.get_items_without_images()
    print(f"\nItems without images: {len(items_without_images)}")
    for item in items_without_images[:5]:  # Show first 5
        print(f"  - {item['name_en']} ({item['category_name']})")
    
    if len(items_without_images) > 5:
        print(f"  ... and {len(items_without_images) - 5} more")


if __name__ == "__main__":
    main()

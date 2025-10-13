from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_file, flash
from database import MenuDatabase
import qrcode
from PIL import Image
import os
from dotenv import load_dotenv
import io
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Email configuration
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')  
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')

# Initialize database
db = MenuDatabase()

def send_email(to_email, subject, body, is_html=False):
    """Send email using Gmail SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

# Language content dictionary
CONTENT = {
    'jp': {
        'site_title': 'タージ | 本場インドの味',
        'nav_home': 'ホーム',
        'nav_about': 'タージについて',
        'nav_contact': 'お問い合わせ',
        'nav_restaurants': 'レストラン',
        'nav_okinawa': '沖縄店',
        'nav_nikko': '日光店',
        'nav_fuji': '河口湖店',
        'welcome': 'ようこそ',
        'welcome_text': 'へ。本格インド料理を日本でお楽しみください。',
        'welcome_desc': 'タージは日本で本格的なインド料理を提供するレストランチェーンです。',
        'branches': '支店',
        'branch_title': '私たちのレストラン',
        'features': '特徴',
        'our_features': '私たちの特徴',
        'contact': '連絡先',
        'highlights': '特徴',
        'menu': 'メニュー',
        'actions': 'アクション',
        'book_table': 'テーブル予約',
        'order_online': 'オンライン注文',
        'view_gallery': 'フォトギャラリー',
        'address': '住所',
        'phone': '電話',
        'hours': '営業時間',
        'map': 'マップ',
        'language': '言語',
        'visit_btn': '店舗を見る',
        'dining': 'お食事',
        'dining_desc': '各レストランのページをご覧ください',
        'reservations': '予約',
        'reservations_desc': 'テーブル予約',
        'delivery': '配達',
        'delivery_desc': 'オンライン注文（Uber Eats / 出前館）',
        'menus': 'メニュー',
        'menus_desc': 'メニュー閲覧（PDF・画像）',
        'location': '場所',
        'location_desc': 'Google マップで検索',
        'social': 'SNS',
        'social_desc': 'Instagram / Facebook でフォロー',
        'taj_okinawa': 'Taj Okinawa',
        'taj_nikko': 'Taj Nikko',
        'taj_fuji': 'Taj Fuji',
        'okinawa_tagline': '本格インド料理',
        'nikko_tagline': '山の静けさ',
        'fuji_tagline': '富士の景色',
        'okinawa_highlights': ['海を望むテラス席', '配達・テイクアウト・予約', '季節の海鮮スペシャル'],
        'nikko_highlights': ['寺院を望むお食事', '居心地の良い内装', 'テイクアウト・予約'],
        'fuji_highlights': ['美しい湖の景色', '洗練された雰囲気', 'テイクアウト・予約'],
        # Restaurant page navigation
        'restaurant_nav_home': 'ホーム',
        'restaurant_nav_menu': 'お料理メニュー',
        'restaurant_nav_takeout': 'テイクアウト・デリバリー',
        'restaurant_nav_gallery': 'フォトギャラリー',
        'restaurant_nav_info': '店舗情報',
        'restaurant_nav_contact': 'お問い合わせ',
        # Restaurant page content
        'dine_in': 'イートイン',
        'takeout_delivery': 'テイクアウト・デリバリー',
        'menu_sections': 'メニュー',
        'takeout_menu': 'テイクアウト・デリバリーメニュー',
        'lunch_menu': 'ランチメニュー',
        'grand_menu': '通常メニュー',
        'store_info': '店舗情報',
        'authentic_cuisine': '本格インド料理をお楽しみください',
        'experience_desc': '経験豊富なシェフが伝統的なレシピで本格的な料理をご提供いたします。香り豊かなカレーから焼きたてのナンまで、厳選された食材で丁寧に調理しています。',
        'view_menu_pdf': 'メニューPDF',
        'view_gallery': 'フォトギャラリー',
        'halal_title': 'ハラール対応',
        'halal_desc': 'ムスリムのお客様にも安心してお食事をお楽しみいただけます。ハラール認証食材を使用しております。',
        'about_us': 'タージについて',
        'about_us_desc': [
            '日本の中心でオーセンティックなインド料理への玄関口、タージへようこそ。',
            '私たちの物語は40年以上前、シンプルな情熱から始まりました：インド料理の豊かな風味と伝統への愛です。過去33年間、私たちの創設者は日本を故郷と呼び、インド料理の技術を完璧にすることに人生を捧げてきました。数十年の経験を持つ彼は、私たちが提供するすべての料理に深い知識、技術、そして心のこもったコミットメントをもたらします。',
            'タージでは、食事は単なる食事以上のものだと信じています。それは旅なのです。すべてのレシピは新鮮な食材、本格的なスパイス、そして伝統と革新のバランスで作られています。昔ながらの家族のレシピから現代的なタッチを加えた料理まで、私たちはすべてのお客様とインド料理の活気に満ちた多様性を共有することを目指しています。',
            '遺産、情熱、そして真正性の物語をすべての皿が語るタージにぜひお越しください。皆様をお迎えできることを楽しみにしております。'
        ],
    },
    'en': {
        'site_title': 'Taj — Taste of Authentic India',
        'nav_home': 'Home',
        'nav_about': 'About Us',
        'nav_contact': 'Contact',
        'nav_restaurants': 'Restaurants',
        'nav_okinawa': 'Okinawa',
        'nav_nikko': 'Nikko',
        'nav_fuji': 'Kawaguchiko',
        'welcome': 'Welcome to',
        'welcome_text': ', a chain of restaurants offering authentic Indian cuisine in Japan.',
        'welcome_desc': 'Taj is a chain of restaurants offering authentic Indian cuisine in Japan.',
        'branches': 'Branches',
        'branch_title': 'Our Restaurants',
        'features': 'Features',
        'our_features': 'Our Features',
        'contact': 'Contact',
        'highlights': 'Highlights',
        'menu': 'Menu',
        'actions': 'Actions',
        'book_table': 'Book a Table',
        'order_online': 'Order Online',
        'view_gallery': 'View Gallery',
        'address': 'Address',
        'phone': 'Phone',
        'hours': 'Hours',
        'map': 'Map',
        'language': 'Language',
        'visit_btn': 'Visit',
        'dining': 'Dining',
        'dining_desc': 'View each restaurant\'s page',
        'reservations': 'Reservations',
        'reservations_desc': 'Book a table',
        'delivery': 'Delivery',
        'delivery_desc': 'Order online (Uber Eats / 出前館)',
        'menus': 'Menus',
        'menus_desc': 'Browse menus (PDF & images)',
        'location': 'Location',
        'location_desc': 'Find us on Google Maps',
        'social': 'Social',
        'social_desc': 'Follow us on Instagram / Facebook',
        'taj_okinawa': 'Taj Okinawa',
        'taj_nikko': 'Taj Nikko',
        'taj_fuji': 'Taj Fuji',
        'okinawa_tagline': 'Taste of Authentic India',
        'nikko_tagline': 'Taste of Authentic India',
        'fuji_tagline': 'Taste of Authentic India',
        'okinawa_highlights': ['Terrace dining with sea view', 'Delivery / Takeout / Reservations', 'Seasonal seafood specials'],
        'nikko_highlights': ['Temple-view dining', 'Cozy interiors', 'Takeout / Reservations'],
        'fuji_highlights': ['Scenic lake views', 'Refined atmosphere', 'Takeout / Reservations'],
        # Restaurant page navigation
        'restaurant_nav_home': 'Home',
        'restaurant_nav_menu': 'Food Menu',
        'restaurant_nav_takeout': 'Takeout Delivery',
        'restaurant_nav_gallery': 'Photo Gallery',
        'restaurant_nav_info': 'Information',
        'restaurant_nav_contact': 'Contact',
        # Restaurant page content
        'dine_in': 'Dine In',
        'takeout_delivery': 'Takeout & Delivery',
        'menu_sections': 'Menu',
        'takeout_menu': 'Take Out & Delivery Menu',
        'lunch_menu': 'Lunch Menu',
        'grand_menu': 'Grand Menu',
        'store_info': 'Store Information',
        'authentic_cuisine': 'Experience Authentic Indian Cuisine',
        'experience_desc': 'Our chefs bring years of experience and traditional recipes to create an authentic dining experience. From aromatic curries to freshly baked naan, every dish is prepared with care and the finest ingredients.',
        'view_menu_pdf': 'View Menu PDF',
        'view_gallery': 'View Photo Gallery',
        'halal_title': 'Halal Certified',
        'halal_desc': 'We welcome Muslim guests with confidence. We use halal-certified ingredients for your peace of mind.',
        'about_us': 'About Us',
        'about_us_desc': [
            'Welcome to Taj — your gateway to authentic Indian cuisine in the heart of Japan.',
            'Our story began over 40 years ago with a simple passion: a love for the rich flavors and traditions of Indian cooking. For the past 33 years, our founder has called Japan home, dedicating his life to perfecting the art of Indian cuisine. With decades of experience, he brings deep knowledge, skill, and a heartfelt commitment to every dish we serve.',
            'At Taj, we believe food is more than a meal — it\'s a journey. Every recipe is crafted with fresh ingredients, authentic spices, and a balance of tradition and innovation. From timeless family recipes to dishes with a modern touch, we aim to share the vibrant diversity of Indian cuisine with every guest.',
            'Join us at Taj, where every plate tells a story of heritage, passion, and authenticity. We look forward to welcoming you.'
        ],
    }
}

def get_language():
    """Get current language from session, default to Japanese"""
    return session.get('language', 'jp')

def get_content(key=None):
    """Get content for current language"""
    lang = get_language()
    if key:
        return CONTENT[lang].get(key, key)
    return CONTENT[lang]

@app.route('/set_language/<language>')
def set_language(language):
    """Set language preference"""
    if language in ['en', 'jp']:
        session['language'] = language
    return redirect(request.referrer or url_for('homepage'))

@app.route('/')
def homepage():
    """Homepage showing all Taj restaurant branches"""
    return render_template('index.html', content=get_content(), lang=get_language(), is_restaurant_page=False)

@app.route('/about')
def about_page():
    """About us page"""
    return render_template('about.html', content=get_content(), lang=get_language(), is_restaurant_page=False)

@app.route('/contact', methods=['GET', 'POST'])
def contact_page():
    """Main contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        message = request.form.get('message', '')
        reservation_type = request.form.get('reservation_type', 'contact')
        
        if reservation_type == 'contact':
            # Regular contact form
            if email and message:
                subject = f"New Contact Form Submission from {first_name} {last_name}"
                body = f"""
New contact form submission:

Name: {first_name} {last_name}
Email: {email}
Phone: {phone}
Message: {message}

Submitted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                
                if send_email(EMAIL_ADDRESS, subject, body):
                    flash('Thank you for your message! We will get back to you soon.', 'success')
                else:
                    flash('Sorry, there was an error sending your message. Please try again.', 'error')
            else:
                flash('Please fill in all required fields.', 'error')
        
        elif reservation_type in ['individual', 'travel_agency']:
            # Reservation form submission
            restaurant_location = request.form.get('restaurant_location', '')
            reservation_date = request.form.get('reservation_date', '')
            reservation_time = request.form.get('reservation_time', '')
            representative_name = request.form.get('representative_name', '')
            group_name = request.form.get('group_name', '')
            guest_count = request.form.get('guest_count', '')
            dining_preference = request.form.get('dining_preference', '')
            transportation = request.form.get('transportation', '')
            parking_spaces = request.form.get('parking_spaces', '')
            notes = request.form.get('notes', '')
            
            # Travel agency specific fields
            travel_agency_name = request.form.get('travel_agency_name', '')
            travel_agency_contact = request.form.get('travel_agency_contact', '')
            bus_company = request.form.get('bus_company', '')
            driver_count = request.form.get('driver_count', '')
            driver_meals = request.form.get('driver_meals', '')
            guide_count = request.form.get('guide_count', '')
            guide_meals = request.form.get('guide_meals', '')
            
            if email and restaurant_location and reservation_date and reservation_time:
                # Create reservation email
                restaurant_names = {
                    'nikko': 'Taj Nikko (日光店)',
                    'fuji': 'Taj Fuji (河口湖店)',
                    'okinawa': 'Taj Okinawa (沖縄店)'
                }
                
                subject = f"New {reservation_type.replace('_', ' ').title()} Reservation - {restaurant_names.get(restaurant_location, restaurant_location)}"
                
                body = f"""
New {reservation_type.replace('_', ' ').title()} Reservation:

Restaurant: {restaurant_names.get(restaurant_location, restaurant_location)}
Date: {reservation_date}
Time: {reservation_time}
Representative: {representative_name}
Group Name: {group_name}
Guest Count: {guest_count}
Dining Preference: {dining_preference}
Transportation: {transportation}
Parking Spaces: {parking_spaces}
Notes: {notes}

Contact Information:
Email: {email}
Phone: {phone}

"""
                
                if reservation_type == 'travel_agency':
                    body += f"""
Travel Agency Information:
Agency Name: {travel_agency_name}
Contact Person: {travel_agency_contact}
Bus Company: {bus_company}
Driver Count: {driver_count}
Driver Meals: {driver_meals}
Guide Count: {guide_count}
Guide Meals: {guide_meals}

"""
                
                body += f"Submitted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                if send_email(EMAIL_ADDRESS, subject, body):
                    flash('Thank you for your reservation! We will confirm your booking soon.', 'success')
                else:
                    flash('Sorry, there was an error processing your reservation. Please try again.', 'error')
            else:
                flash('Please fill in all required fields.', 'error')
        
        return redirect(url_for('contact_page'))
    
    return render_template('main-contact.html', content=get_content(), lang=get_language(), is_restaurant_page=False)

@app.route('/reservations', methods=['GET', 'POST'])
def reservations_page():
    """Reservations page"""
    if request.method == 'POST':
        # Handle reservation form submission
        reservation_type = request.form.get('reservation_type', 'individual')
        restaurant_location = request.form.get('restaurant_location', '')
        reservation_date = request.form.get('reservation_date', '')
        reservation_time = request.form.get('reservation_time', '')
        representative_name = request.form.get('representative_name', '')
        group_name = request.form.get('group_name', '')
        guest_count = request.form.get('guest_count', '')
        dining_preference = request.form.get('dining_preference', '')
        transportation = request.form.get('transportation', '')
        parking_spaces = request.form.get('parking_spaces', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        postal_code = request.form.get('postal_code', '')
        address = request.form.get('address', '')
        notes = request.form.get('notes', '')
        
        # Travel agency specific fields
        travel_agency_name = request.form.get('travel_agency_name', '')
        travel_agency_contact = request.form.get('travel_agency_contact', '')
        bus_company = request.form.get('bus_company', '')
        driver_count = request.form.get('driver_count', '')
        driver_meals = request.form.get('driver_meals', '')
        guide_count = request.form.get('guide_count', '')
        guide_meals = request.form.get('guide_meals', '')
        
        if email and restaurant_location and reservation_date and reservation_time:
            # Create reservation email
            restaurant_names = {
                'nikko': 'Taj Nikko (日光店)',
                'fuji': 'Taj Fuji (河口湖店)',
                'okinawa': 'Taj Okinawa (沖縄店)'
            }
            
            subject = f"New {reservation_type.replace('_', ' ').title()} Reservation - {restaurant_names.get(restaurant_location, restaurant_location)}"
            
            body = f"""
New {reservation_type.replace('_', ' ').title()} Reservation:

Restaurant: {restaurant_names.get(restaurant_location, restaurant_location)}
Date: {reservation_date}
Time: {reservation_time}
Representative: {representative_name}
Group Name: {group_name}
Guest Count: {guest_count}
Dining Preference: {dining_preference}
Transportation: {transportation}
Parking Spaces: {parking_spaces}
Notes: {notes}

Contact Information:
Email: {email}
Phone: {phone}
Postal Code: {postal_code}
Address: {address}

"""
            
            if reservation_type == 'travel_agency':
                body += f"""
Travel Agency Information:
Agency Name: {travel_agency_name}
Contact Person: {travel_agency_contact}
Bus Company: {bus_company}
Driver Count: {driver_count}
Driver Meals: {driver_meals}
Guide Count: {guide_count}
Guide Meals: {guide_meals}

"""
            
            body += f"Submitted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            if send_email(EMAIL_ADDRESS, subject, body):
                flash('Thank you for your reservation! We will confirm your booking soon.', 'success')
            else:
                flash('Sorry, there was an error processing your reservation. Please try again.', 'error')
        else:
            flash('Please fill in all required fields.', 'error')
        
        return redirect(url_for('reservations_page'))
    
    return render_template('reservations.html', content=get_content(), lang=get_language(), is_restaurant_page=False)

@app.route('/taj-okinawa')
def taj_okinawa():
    """Taj Okinawa restaurant page"""
    restaurant_data = {
        'name': 'Taj Okinawa',
        'tagline_en': 'Taste of Authentic India',
        'tagline_jp': '本格インド料理',
        'address': '〒904-0102 Okinawa, Nakagami District, Chatan, Ihei, 458-1 イーグルロッジ 1F',
        'phone': '098-923-1312',
        'hours_dine': '11:00 – 22:00',
        'hours_delivery': '11:00 – 21:30',
        'location': 'okinawa'
    }
    return render_template('restaurant.html', restaurant=restaurant_data, content=get_content(), lang=get_language(), is_restaurant_page=True)

@app.route('/taj-nikko')
def taj_nikko():
    """Taj Nikko restaurant page"""
    restaurant_data = {
        'name': 'Taj Nikko',
        'tagline_en': 'Taste of Authentic India',
        'tagline_jp': '本格インド料理',
        'address': '2F, 2-32 Honcho, Nikko, Tochigi 321-1434',
        'phone': '0288-25-7766',
        'hours_dine': '11:00 – 21:00',
        'hours_delivery': '11:00 – 21:00',
        'location': 'nikko'
    }
    return render_template('restaurant.html', restaurant=restaurant_data, content=get_content(), lang=get_language(), is_restaurant_page=True)

@app.route('/taj-fuji')
def taj_fuji():
    """Taj Kawaguchiko restaurant page"""
    restaurant_data = {
        'name': 'Taj Fuji',
        'tagline_en': 'Taste of Authentic India',
        'tagline_jp': '本格インド料理',
        'address': '〒904-0102 Okinawa, Nakagami District, Chatan, Ihei, 458-1 イーグルロッジ 1F',
        'phone': '098-923-1312',
        'hours_dine': '11:00 – 22:00',
        'hours_delivery': '11:00 – 21:30',
        'location': 'fuji'
    }
    return render_template('restaurant.html', restaurant=restaurant_data, content=get_content(), lang=get_language(), is_restaurant_page=True)

# Restaurant sub-pages routes
@app.route('/taj-<location>/menu')
def restaurant_menu(location):
    """Restaurant menu page"""
    restaurant_data = get_restaurant_data(location)
    
    # Get menu data from database for okinawa, nikko and fuji
    menu_data = None
    if location in ['okinawa', 'nikko', 'fuji']:
        menu_data = db.get_menu_by_location(location)
    
    return render_template('food-menu.html', 
                         restaurant=restaurant_data, 
                         content=get_content(), 
                         lang=get_language(), 
                         is_restaurant_page=True,
                         menu_data=menu_data)

@app.route('/taj-<location>/takeout')
def restaurant_takeout(location):
    """Restaurant takeout/delivery page"""
    restaurant_data = get_restaurant_data(location)
    return render_template('takeout-delivery.html', restaurant=restaurant_data, content=get_content(), lang=get_language(), is_restaurant_page=True)

@app.route('/taj-<location>/gallery')
def restaurant_gallery(location):
    """Restaurant photo gallery page"""
    restaurant_data = get_restaurant_data(location)
    
    # Get gallery images for the location
    gallery_images = get_gallery_images(location)
    
    return render_template('gallery.html', 
                         restaurant=restaurant_data, 
                         content=get_content(), 
                         lang=get_language(), 
                         is_restaurant_page=True,
                         gallery_images=gallery_images)

@app.route('/taj-<location>/information')
def restaurant_information(location):
    """Restaurant information page"""
    restaurant_data = get_restaurant_data(location)
    return render_template('information.html', restaurant=restaurant_data, content=get_content(), lang=get_language(), is_restaurant_page=True)

@app.route('/taj-<location>/contact')
def restaurant_contact(location):
    """Restaurant contact page"""
    restaurant_data = get_restaurant_data(location)
    return render_template('contact.html', restaurant=restaurant_data, content=get_content(), lang=get_language(), is_restaurant_page=True)

def get_gallery_images(location):
    """Get gallery images for a specific restaurant location"""
    import glob
    
    # Define gallery folders for each location
    gallery_folders = {
        'nikko': 'taj_nikko_gallery',
        'okinawa': 'taj_okinawa_gallery',  # For future use
        'fuji': 'taj_fuji_gallery'  # For future use
    }
    
    gallery_folder = gallery_folders.get(location)
    if not gallery_folder:
        return []
    
    # Get all image files from the gallery folder
    gallery_path = os.path.join(app.static_folder, 'images', gallery_folder)
    
    if not os.path.exists(gallery_path):
        return []
    
    # Get all webp, jpg, jpeg, png files
    image_extensions = ['*.webp', '*.jpg', '*.jpeg', '*.png']
    images = []
    
    for extension in image_extensions:
        pattern = os.path.join(gallery_path, extension)
        found_images = glob.glob(pattern)
        images.extend(found_images)
    
    # Convert to relative paths and sort
    gallery_images = []
    for img_path in sorted(images):
        relative_path = os.path.relpath(img_path, app.static_folder)
        # Convert to URL format
        url_path = relative_path.replace('\\', '/')
        gallery_images.append({
            'url': url_for('static', filename=url_path),
            'filename': os.path.basename(img_path),
            'alt': f"{location.title()} Restaurant Gallery Image"
        })
    
    return gallery_images

def get_restaurant_data(location):
    """Get restaurant data based on location"""
    restaurants = {
        'okinawa': {
            'name': 'Taj Okinawa',
            'tagline_en': 'Taste of Authentic India',
            'tagline_jp': '本格インド料理',
            'address': '〒904-0102 Okinawa, Nakagami District, Chatan, Ihei, 458-1 イーグルロッジ 1F',
            'phone': '098-923-1312',
            'hours_dine': '11:00 – 22:00',
            'hours_delivery': '11:00 – 21:30',
            'location': 'okinawa'
        },
        'nikko': {
            'name': 'Taj Nikko',
            'tagline_en': 'Taste of Authentic India',
            'tagline_jp': '本格インド料理',
            'address': '2F, 2-32 Honcho, Nikko, Tochigi 321-1434',
            'phone': '0288-25-7766',
            'hours_dine': '11:00 – 21:00',
            'hours_delivery': '11:00 – 21:00',
            'location': 'nikko'
        },
        'fuji': {
            'name': 'Taj Fuji',
            'tagline_en': 'Taste of Authentic India',
            'tagline_jp': '本格インド料理',
            'address': '〒904-0102 Okinawa, Nakagami District, Chatan, Ihei, 458-1 イーグルロッジ 1F',
            'phone': '098-923-1312',
            'hours_dine': '11:00 – 22:00',
            'hours_delivery': '11:00 – 21:30',
            'location': 'fuji'
        }
    }
    return restaurants.get(location, restaurants['okinawa'])

# Admin routes for menu management
@app.route('/admin/menu')
def admin_menu():
    """Simple admin interface for menu management"""
    items_without_images = db.get_items_without_images()
    return render_template('admin_menu.html', items=items_without_images)

@app.route('/admin/set-menus')
def admin_set_menus():
    """Admin interface for managing set menus"""
    set_menus = db.get_all_set_menus()
    return render_template('admin_set_menus.html', set_menus=set_menus)

@app.route('/admin/menu/update_image/<int:item_id>', methods=['POST'])
def update_menu_image(item_id):
    """Update menu item image"""
    image_path = request.form.get('image_url')  # This is actually the path now
    image_alt = request.form.get('image_alt')
    
    if image_path:
        # Convert the path to a proper Flask static URL
        # Remove 'static/' prefix if user included it
        if image_path.startswith('static/'):
            image_path = image_path[7:]  # Remove 'static/' prefix
        elif image_path.startswith('/static/'):
            image_path = image_path[8:]  # Remove '/static/' prefix
        
        # Generate the proper Flask URL
        image_url = url_for('static', filename=image_path)
        db.update_menu_item_image(item_id, image_url, image_alt)
    
    return redirect(url_for('admin_menu'))

@app.route('/admin/set-menus/update_location/<int:set_id>', methods=['POST'])
def update_set_menu_location(set_id):
    """Update set menu restaurant location"""
    restaurant_location = request.form.get('restaurant_location')
    
    if restaurant_location:
        db.update_set_menu_restaurant_location(set_id, restaurant_location)
    
    return redirect(url_for('admin_set_menus'))

@app.route('/api/create-order', methods=['POST'])
def create_order():
    """Create a new order and generate QR code"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'items' not in data or 'total_amount' not in data:
            return jsonify({'error': 'Invalid order data'}), 400
        
        # Add restaurant location from session or request
        restaurant_location = data.get('restaurant_location', session.get('current_restaurant', 'unknown'))
        
        order_data = {
            'items': data['items'],
            'total_amount': data['total_amount'],
            'restaurant_location': restaurant_location,
            'customer_info': data.get('customer_info', {})
        }
        
        # Create order in database
        order_number = db.create_order(order_data)
        
        # Generate QR code
        qr_code_url = generate_qr_code(order_number)
        
        return jsonify({
            'success': True,
            'order_number': order_number,
            'qr_code_url': qr_code_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_qr_code(order_number):
    """Generate QR code for order (in-memory only, no file saving)"""
    # Generate QR code data (just the order number)
    qr_data = order_number
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image in memory
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert image to base64 string for inline display
    import io
    import base64
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    # Return data URL for inline display
    return f"data:image/png;base64,{img_str}"

@app.route('/admin/orders')
def admin_orders():
    """Admin interface for viewing pending orders"""
    try:
        pending_orders = db.get_pending_orders()
        print(f"DEBUG: pending_orders type: {type(pending_orders)}")
        print(f"DEBUG: pending_orders length: {len(pending_orders) if hasattr(pending_orders, '__len__') else 'no length'}")
        return render_template('admin_orders.html', orders=pending_orders)
    except Exception as e:
        print(f"ERROR in admin_orders: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/admin/orders/<restaurant_location>')
def admin_orders_by_location(restaurant_location):
    """Admin interface for viewing pending orders by restaurant location"""
    try:
        pending_orders = db.get_pending_orders_by_location(restaurant_location)
        print(f"DEBUG: pending_orders for {restaurant_location} type: {type(pending_orders)}")
        print(f"DEBUG: pending_orders length: {len(pending_orders) if hasattr(pending_orders, '__len__') else 'no length'}")
        return render_template('admin_orders.html', orders=pending_orders, restaurant_location=restaurant_location)
    except Exception as e:
        print(f"ERROR in admin_orders_by_location: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/admin/order/<order_number>')
def view_order(order_number):
    """View specific order details"""
    try:
        order = db.get_order(order_number)
        print(f"Looking up order: {order_number}")
        print(f"Order found: {order is not None}")
        
        if not order:
            print(f"Order {order_number} not found in database")
            return "Order not found", 404
        
        print(f"Order status: {order.get('status')}")
        
        # Only show orders with 'new' status in the collect interface
        # Already processed orders should not be shown
        if order.get('status') not in ['new', 'pending']:
            print(f"Order {order_number} already processed (status: {order.get('status')})")
            return "Order already processed", 404
        
        # Convert item names to English for staff viewing
        for item in order['items']:
            if 'id' in item and 'type' in item:
                english_name = db.get_english_name_for_item(item['id'], item.get('type', 'menu_item'))
                if english_name:
                    item['name'] = english_name
        
        return render_template('order_details.html', order=order)
    except Exception as e:
        print(f"Error in view_order: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading order: {str(e)}", 500

@app.route('/admin/order/<order_number>/complete', methods=['POST'])
def complete_order(order_number):
    """Mark order as completed"""
    db.update_order_status(order_number, 'completed')
    return redirect(url_for('admin_orders'))

@app.route('/admin/order/<order_number>/complete/<restaurant_location>', methods=['POST'])
def complete_order_by_location(order_number, restaurant_location):
    """Mark order as completed and redirect to location-specific orders"""
    db.update_order_status(order_number, 'completed')
    return redirect(url_for('admin_orders_by_location', restaurant_location=restaurant_location))

@app.route('/admin/collect-order')
def collect_order():
    """QR code scanner interface for collecting orders"""
    return render_template('collect_order.html')

@app.route('/admin/collect-order/<restaurant_location>')
def collect_order_by_location(restaurant_location):
    """QR code scanner interface for collecting orders by restaurant location"""
    return render_template('collect_order.html', restaurant_location=restaurant_location)

@app.route('/admin/order/<order_number>/accept', methods=['POST'])
def accept_order(order_number):
    """Accept an order (move to pending status)"""
    db.update_order_status(order_number, 'pending')
    return jsonify({'success': True, 'message': 'Order accepted'})

@app.route('/admin/order/<order_number>/reject', methods=['POST'])
def reject_order(order_number):
    """Reject an order (move to rejected status)"""
    db.update_order_status(order_number, 'rejected')
    return jsonify({'success': True, 'message': 'Order rejected'})

@app.route('/staff/orders')
def staff_orders():
    """Staff interface for viewing new orders that need approval"""
    try:
        new_orders = db.get_orders_by_status('new')
        print(f"DEBUG: new_orders type: {type(new_orders)}")
        print(f"DEBUG: new_orders length: {len(new_orders) if hasattr(new_orders, '__len__') else 'no length'}")
        return render_template('staff_orders.html', orders=new_orders)
    except Exception as e:
        print(f"ERROR in staff_orders: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/api/gallery-images/<location>')
def api_gallery_images(location):
    """API endpoint to get gallery images for a specific location"""
    try:
        gallery_images = get_gallery_images(location)
        return jsonify(gallery_images)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/menu-items')
def api_menu_items():
    """API endpoint to get menu items by category"""
    try:
        import sqlite3
        category = request.args.get('category')
        categories = request.args.get('categories')  # Support multiple categories
        
        conn = sqlite3.connect('taj_menu.db')
        cursor = conn.cursor()
        
        if categories:
            # Handle multiple categories (comma-separated)
            category_list = categories.split(',')
            placeholders = ','.join('?' * len(category_list))
            query = f'SELECT id, name_en, price FROM menu_items WHERE category_id IN ({placeholders})'
            print(f"Executing query: {query} with params: {category_list}")
            cursor.execute(query, category_list)
        elif category:
            cursor.execute('SELECT id, name_en, price FROM menu_items WHERE category_id = ?', (category,))
        else:
            cursor.execute('SELECT id, name_en, price FROM menu_items')
        
        items = []
        for row in cursor.fetchall():
            items.append({
                'id': str(row[0]),
                'name': row[1],
                'price': row[2]
            })
        
        conn.close()
        print(f"Returning {len(items)} items: {items}")
        return jsonify(items)
    except Exception as e:
        print(f"Error in api_menu_items: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    localhost = '0.0.0.0'
    # For HTTPS with self-signed certificate 
    app.run(port=5200, debug=True, host=localhost, ssl_context='adhoc')

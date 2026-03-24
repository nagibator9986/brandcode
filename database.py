import sqlite3
import os
from werkzeug.security import generate_password_hash
import random

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'brandcode.db')


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            icon TEXT,
            image_url TEXT,
            sort_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            old_price INTEGER,
            category_id INTEGER,
            brand TEXT,
            gender TEXT DEFAULT 'unisex',
            is_active INTEGER DEFAULT 1,
            is_featured INTEGER DEFAULT 0,
            is_new INTEGER DEFAULT 0,
            is_sale INTEGER DEFAULT 0,
            video_url TEXT,
            instagram_video_url TEXT,
            views_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS product_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            is_main INTEGER DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS product_sizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            size TEXT NOT NULL,
            quantity INTEGER DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            customer_phone TEXT,
            customer_city TEXT,
            delivery_method TEXT,
            items_json TEXT NOT NULL,
            total_amount INTEGER NOT NULL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, product_id),
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS site_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS promo_banners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            subtitle TEXT,
            image_url TEXT,
            link TEXT,
            is_active INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            logo_url TEXT,
            is_active INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0
        );
    ''')

    # Check if data already seeded
    existing = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    if existing == 0:
        seed_data(db)

    db.commit()
    db.close()


def seed_data(db):
    # ========== Admin user ==========
    password_hash = generate_password_hash('admin123')
    db.execute(
        "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
        ('admin', password_hash)
    )

    # ========== Categories ==========
    categories = [
        ('Футболки', 'futbolki', 'fa-tshirt', 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&h=400&fit=crop', 1),
        ('Худи и свитшоты', 'hudi-i-svitshoty', 'fa-hoodie', 'https://images.unsplash.com/photo-1556821840-3a0e5bb01f0e?w=600&h=400&fit=crop', 2),
        ('Куртки', 'kurtki', 'fa-jacket', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&h=400&fit=crop', 3),
        ('Штаны', 'shtany', 'fa-pants', 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&h=400&fit=crop', 4),
        ('Кроссовки', 'krossovki', 'fa-shoe-prints', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&h=400&fit=crop', 5),
        ('Аксессуары', 'aksessuary', 'fa-glasses', 'https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=600&h=400&fit=crop', 6),
    ]
    for name, slug, icon, image_url, sort_order in categories:
        db.execute(
            "INSERT INTO categories (name, slug, icon, image_url, sort_order) VALUES (?, ?, ?, ?, ?)",
            (name, slug, icon, image_url, sort_order)
        )

    # ========== Products ==========
    products = [
        # Футболки (category_id=1)
        {
            'name': 'Nike Sportswear Essential Футболка',
            'slug': 'nike-sportswear-essential-tee',
            'description': 'Классическая футболка Nike из мягкого хлопка с фирменным логотипом Swoosh на груди. Свободный крой обеспечивает комфорт на каждый день. Идеально подходит для создания повседневного стритвир-образа.',
            'price': 18500,
            'old_price': None,
            'category_id': 1,
            'brand': 'Nike',
            'gender': 'unisex',
            'is_featured': 1,
            'is_new': 1,
            'is_sale': 0,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Off-White Arrows Oversize Футболка',
            'slug': 'off-white-arrows-oversize-tee',
            'description': 'Культовая футболка Off-White с принтом перекрещенных стрелок на спине. Оверсайз-силуэт, 100% хлопок. Визитная карточка бренда Вирджила Абло, ставшая символом люксового стритвира.',
            'price': 89000,
            'old_price': 120000,
            'category_id': 1,
            'brand': 'Off-White',
            'gender': 'unisex',
            'is_featured': 1,
            'is_new': 0,
            'is_sale': 1,
            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            'instagram_video_url': None,
        },
        {
            'name': 'Supreme Box Logo Tee',
            'slug': 'supreme-box-logo-tee',
            'description': 'Легендарная футболка Supreme с культовым бокс-логотипом. Коллекционная вещь, которая никогда не выходит из моды. Плотный хлопок, прямой крой. Маст-хэв для любого поклонника стритвир-культуры.',
            'price': 65000,
            'old_price': None,
            'category_id': 1,
            'brand': 'Supreme',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 1,
            'is_sale': 0,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Stussy Basic Logo Tee',
            'slug': 'stussy-basic-logo-tee',
            'description': 'Фирменная футболка Stussy с классическим логотипом на груди. Один из старейших стритвир-брендов. Мягкий хлопок, удобная посадка. Отличный выбор для ежедневной носки.',
            'price': 22000,
            'old_price': 28000,
            'category_id': 1,
            'brand': 'Stussy',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 0,
            'is_sale': 1,
            'video_url': None,
            'instagram_video_url': None,
        },
        # Худи и свитшоты (category_id=2)
        {
            'name': 'Balenciaga Political Campaign Худи',
            'slug': 'balenciaga-political-campaign-hoodie',
            'description': 'Оверсайз-худи Balenciaga из коллекции Political Campaign. Плотный флис, объёмный капюшон, кенгуру-карман. Провокационный дизайн от Демны Гвасалии. Премиальное качество.',
            'price': 245000,
            'old_price': None,
            'category_id': 2,
            'brand': 'Balenciaga',
            'gender': 'unisex',
            'is_featured': 1,
            'is_new': 1,
            'is_sale': 0,
            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            'instagram_video_url': 'https://www.instagram.com/reel/example1/',
        },
        {
            'name': 'Nike Tech Fleece Худи',
            'slug': 'nike-tech-fleece-hoodie',
            'description': 'Технологичное худи Nike Tech Fleece — идеальное сочетание стиля и комфорта. Лёгкий утеплённый флис, эргономичный крой, молния во всю длину. Культовая модель для городского стиля.',
            'price': 42000,
            'old_price': 55000,
            'category_id': 2,
            'brand': 'Nike',
            'gender': 'unisex',
            'is_featured': 1,
            'is_new': 0,
            'is_sale': 1,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Essentials Fear of God Худи',
            'slug': 'essentials-fog-hoodie',
            'description': 'Минималистичное худи из линейки Essentials от Fear of God. Оверсайз-силуэт, утолщённая ткань, рельефный логотип на груди. Нейтральные тона и премиальное качество.',
            'price': 78000,
            'old_price': None,
            'category_id': 2,
            'brand': 'Fear of God',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 1,
            'is_sale': 0,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Adidas Originals Trefoil Свитшот',
            'slug': 'adidas-trefoil-sweatshirt',
            'description': 'Классический свитшот Adidas Originals с крупным логотипом Trefoil. Мягкий French terry, рубчатые манжеты и подол. Ретро-стиль, который актуален всегда.',
            'price': 25000,
            'old_price': 32000,
            'category_id': 2,
            'brand': 'Adidas',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 0,
            'is_sale': 1,
            'video_url': None,
            'instagram_video_url': None,
        },
        # Куртки (category_id=3)
        {
            'name': 'The North Face Nuptse 1996',
            'slug': 'tnf-nuptse-1996',
            'description': 'Культовый пуховик The North Face Nuptse 1996 Retro. Гусиный пух 700 fill, водоотталкивающая ткань. Классический объёмный силуэт, ставший символом стритвир-моды.',
            'price': 125000,
            'old_price': None,
            'category_id': 3,
            'brand': 'The North Face',
            'gender': 'unisex',
            'is_featured': 1,
            'is_new': 0,
            'is_sale': 0,
            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            'instagram_video_url': None,
        },
        {
            'name': 'Off-White Industrial Bomber',
            'slug': 'off-white-industrial-bomber',
            'description': 'Бомбер Off-White с фирменными жёлтыми ремешками Industrial. Нейлон высокой плотности, подкладка из вискозы. Визитная карточка бренда, олицетворяющая дух уличной роскоши.',
            'price': 198000,
            'old_price': 250000,
            'category_id': 3,
            'brand': 'Off-White',
            'gender': 'unisex',
            'is_featured': 1,
            'is_new': 0,
            'is_sale': 1,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Stussy Sherpa Reversible Jacket',
            'slug': 'stussy-sherpa-reversible',
            'description': 'Двусторонняя куртка Stussy с шерпа-подкладкой. Одна сторона — гладкий нейлон, другая — мягкий шерпа-флис. Универсальная и стильная вещь на межсезонье.',
            'price': 58000,
            'old_price': None,
            'category_id': 3,
            'brand': 'Stussy',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 1,
            'is_sale': 0,
            'video_url': None,
            'instagram_video_url': None,
        },
        # Штаны (category_id=4)
        {
            'name': 'Nike Tech Fleece Joggers',
            'slug': 'nike-tech-fleece-joggers',
            'description': 'Джоггеры Nike Tech Fleece — иконическая модель спортивных штанов. Зауженный крой, молнии на карманах, эргономичная конструкция. Идеальный баланс стиля и функциональности.',
            'price': 35000,
            'old_price': 45000,
            'category_id': 4,
            'brand': 'Nike',
            'gender': 'unisex',
            'is_featured': 1,
            'is_new': 0,
            'is_sale': 1,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Balenciaga Track Pants',
            'slug': 'balenciaga-track-pants',
            'description': 'Спортивные штаны Balenciaga из нейлона с фирменной вышивкой логотипа. Широкий прямой крой, эластичный пояс на шнурке. Люксовый подход к спортивной эстетике.',
            'price': 145000,
            'old_price': None,
            'category_id': 4,
            'brand': 'Balenciaga',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 1,
            'is_sale': 0,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Adidas Originals Firebird Штаны',
            'slug': 'adidas-firebird-pants',
            'description': 'Классические штаны Adidas Originals Firebird с тремя полосками по бокам. Иконический ретро-дизайн. Трикотаж, зауженный крой, молнии на щиколотках.',
            'price': 19500,
            'old_price': 25000,
            'category_id': 4,
            'brand': 'Adidas',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 0,
            'is_sale': 1,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Essentials Fear of God Sweatpants',
            'slug': 'essentials-fog-sweatpants',
            'description': 'Спортивные штаны из линейки Essentials by Fear of God. Широкий расслабленный крой, эластичный пояс, рельефный логотип. Минимализм и премиальный комфорт.',
            'price': 62000,
            'old_price': None,
            'category_id': 4,
            'brand': 'Fear of God',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 1,
            'is_sale': 0,
            'video_url': None,
            'instagram_video_url': None,
        },
        # Кроссовки (category_id=5)
        {
            'name': 'Nike Air Jordan 1 Retro High OG',
            'slug': 'nike-air-jordan-1-retro-high-og',
            'description': 'Легендарные кроссовки Air Jordan 1 Retro High OG — модель, с которой всё началось. Натуральная кожа, культовый силуэт, колорблок-дизайн. Символ сникер-культуры.',
            'price': 95000,
            'old_price': None,
            'category_id': 5,
            'brand': 'Nike',
            'gender': 'unisex',
            'is_featured': 1,
            'is_new': 1,
            'is_sale': 0,
            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            'instagram_video_url': 'https://www.instagram.com/reel/example2/',
        },
        {
            'name': 'Adidas Yeezy Boost 350 V2',
            'slug': 'adidas-yeezy-boost-350-v2',
            'description': 'Кроссовки Adidas Yeezy Boost 350 V2 от Канье Уэста. Технология Boost, Primeknit верх, футуристический дизайн. Одна из самых желанных моделей в мире сникеров.',
            'price': 135000,
            'old_price': 165000,
            'category_id': 5,
            'brand': 'Adidas',
            'gender': 'unisex',
            'is_featured': 1,
            'is_new': 0,
            'is_sale': 1,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Balenciaga Triple S',
            'slug': 'balenciaga-triple-s',
            'description': 'Кроссовки Balenciaga Triple S — модель, которая запустила тренд на «уродливые» кроссовки. Тройная подошва, состаренный эффект, массивный силуэт. Икона luxury streetwear.',
            'price': 225000,
            'old_price': None,
            'category_id': 5,
            'brand': 'Balenciaga',
            'gender': 'unisex',
            'is_featured': 1,
            'is_new': 0,
            'is_sale': 0,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'New Balance 550 White Green',
            'slug': 'new-balance-550-white-green',
            'description': 'Кроссовки New Balance 550 в расцветке White/Green. Ретро-баскетбольный силуэт, переживающий второе рождение. Натуральная кожа, олдскульная подошва, чистый дизайн.',
            'price': 52000,
            'old_price': 68000,
            'category_id': 5,
            'brand': 'New Balance',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 0,
            'is_sale': 1,
            'video_url': None,
            'instagram_video_url': None,
        },
        # Аксессуары (category_id=6)
        {
            'name': 'Supreme x The North Face Поясная сумка',
            'slug': 'supreme-tnf-waist-bag',
            'description': 'Поясная сумка из коллаборации Supreme x The North Face. Прочный нейлон, несколько отделений, регулируемый ремень. Коллекционная вещь для ценителей стритвир-коллабораций.',
            'price': 45000,
            'old_price': None,
            'category_id': 6,
            'brand': 'Supreme',
            'gender': 'unisex',
            'is_featured': 1,
            'is_new': 1,
            'is_sale': 0,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Off-White Industrial Belt',
            'slug': 'off-white-industrial-belt',
            'description': 'Культовый ремень Off-White Industrial с жёлтой тесьмой и чёрной застёжкой. Длина 200 см, характерная маркировка. Один из самых узнаваемых аксессуаров в мире моды.',
            'price': 38000,
            'old_price': 48000,
            'category_id': 6,
            'brand': 'Off-White',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 0,
            'is_sale': 1,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Balenciaga Explorer Рюкзак',
            'slug': 'balenciaga-explorer-backpack',
            'description': 'Компактный рюкзак Balenciaga Explorer из нейлона с вышитым логотипом. Минималистичный дизайн, функциональные карманы. Люксовый аксессуар для города.',
            'price': 175000,
            'old_price': None,
            'category_id': 6,
            'brand': 'Balenciaga',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 1,
            'is_sale': 0,
            'video_url': None,
            'instagram_video_url': None,
        },
        {
            'name': 'Stussy Stock Кепка',
            'slug': 'stussy-stock-cap',
            'description': 'Бейсболка Stussy Stock с вышитым логотипом на фронтальной панели. Регулируемая застёжка, изогнутый козырёк. Базовый аксессуар для стритвир-гардероба.',
            'price': 15000,
            'old_price': None,
            'category_id': 6,
            'brand': 'Stussy',
            'gender': 'unisex',
            'is_featured': 0,
            'is_new': 0,
            'is_sale': 0,
            'video_url': None,
            'instagram_video_url': None,
        },
    ]

    # ========== Brands ==========
    brand_names = [
        'Nike', 'Adidas', 'Off-White', 'Balenciaga', 'Supreme',
        'Stussy', 'Fear of God', 'The North Face', 'New Balance',
        'Jordan', 'Comme des Garcons', 'Stone Island',
    ]
    for idx, bname in enumerate(brand_names):
        db.execute(
            "INSERT INTO brands (name, sort_order) VALUES (?, ?)",
            (bname, idx)
        )

    # Unsplash image IDs per product (3 unique IDs each, 24 products = 72 images)
    product_image_ids = [
        # Product 1 - Nike Sportswear Essential Tee
        ['1521572163474-6864f9cf17ab', '1576566588028-4147f3842f27', '1503341504253-dff4f94032fc'],
        # Product 2 - Off-White Arrows Oversize Tee
        ['1529374255404-311a2a4f1fd9', '1562157873-818bc0726f68', '1583743814966-8936f5b7be1a'],
        # Product 3 - Supreme Box Logo Tee
        ['1523381210434-271e8be1f52b', '1618354691373-d851c5c3a990', '1594938298603-c8148c4dae35'],
        # Product 4 - Stussy Basic Logo Tee
        ['1583743814966-8936f5b7be1a', '1571945153237-4929e783af4a', '1618354691373-d851c5c3a990'],
        # Product 5 - Balenciaga Political Campaign Hoodie
        ['1556821840-3a0e5bb01f0e', '1578587018452-892bacefd3f2', '1515886657613-9f3515b0c78f'],
        # Product 6 - Nike Tech Fleece Hoodie
        ['1515886657613-9f3515b0c78f', '1556821840-3a0e5bb01f0e', '1578587018452-892bacefd3f2'],
        # Product 7 - Essentials Fear of God Hoodie
        ['1578587018452-892bacefd3f2', '1515886657613-9f3515b0c78f', '1556821840-3a0e5bb01f0e'],
        # Product 8 - Adidas Originals Trefoil Sweatshirt
        ['1556821840-3a0e5bb01f0e', '1578587018452-892bacefd3f2', '1515886657613-9f3515b0c78f'],
        # Product 9 - The North Face Nuptse 1996
        ['1551028719-00167b16eac5', '1544022613-e87ca75a784a', '1591047139829-d91aecb6caea'],
        # Product 10 - Off-White Industrial Bomber
        ['1544022613-e87ca75a784a', '1591047139829-d91aecb6caea', '1551028719-00167b16eac5'],
        # Product 11 - Stussy Sherpa Reversible Jacket
        ['1591047139829-d91aecb6caea', '1551028719-00167b16eac5', '1544022613-e87ca75a784a'],
        # Product 12 - Nike Tech Fleece Joggers
        ['1542272604-787c3835535d', '1624378441864-6eda5145d77b', '1473966968600-fa801b869a1a'],
        # Product 13 - Balenciaga Track Pants
        ['1624378441864-6eda5145d77b', '1473966968600-fa801b869a1a', '1542272604-787c3835535d'],
        # Product 14 - Adidas Originals Firebird Pants
        ['1473966968600-fa801b869a1a', '1542272604-787c3835535d', '1624378441864-6eda5145d77b'],
        # Product 15 - Essentials Fear of God Sweatpants
        ['1542272604-787c3835535d', '1624378441864-6eda5145d77b', '1473966968600-fa801b869a1a'],
        # Product 16 - Nike Air Jordan 1 Retro High OG
        ['1542291026-7eec264c27ff', '1460353581996-0101666a33cc', '1549298916-b41d501d3772'],
        # Product 17 - Adidas Yeezy Boost 350 V2
        ['1460353581996-0101666a33cc', '1549298916-b41d501d3772', '1542291026-7eec264c27ff'],
        # Product 18 - Balenciaga Triple S
        ['1549298916-b41d501d3772', '1542291026-7eec264c27ff', '1460353581996-0101666a33cc'],
        # Product 19 - New Balance 550 White Green
        ['1542291026-7eec264c27ff', '1460353581996-0101666a33cc', '1549298916-b41d501d3772'],
        # Product 20 - Supreme x TNF Waist Bag
        ['1523170335258-f5ed11844a49', '1509941943733-cb0488074d72', '1553062407-98eeb64c6a62'],
        # Product 21 - Off-White Industrial Belt
        ['1509941943733-cb0488074d72', '1553062407-98eeb64c6a62', '1523170335258-f5ed11844a49'],
        # Product 22 - Balenciaga Explorer Backpack
        ['1553062407-98eeb64c6a62', '1523170335258-f5ed11844a49', '1509941943733-cb0488074d72'],
        # Product 23 - Stussy Stock Cap
        ['1523170335258-f5ed11844a49', '1553062407-98eeb64c6a62', '1509941943733-cb0488074d72'],
        # Product 24 (extra safety)
        ['1521572163474-6864f9cf17ab', '1576566588028-4147f3842f27', '1503341504253-dff4f94032fc'],
    ]

    clothing_sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
    shoe_sizes = ['38', '39', '40', '41', '42', '43', '44', '45', '46']

    for idx, p in enumerate(products):
        db.execute(
            """INSERT INTO products
            (name, slug, description, price, old_price, category_id, brand, gender,
             is_featured, is_new, is_sale, video_url, instagram_video_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (p['name'], p['slug'], p['description'], p['price'], p['old_price'],
             p['category_id'], p['brand'], p['gender'],
             p['is_featured'], p['is_new'], p['is_sale'],
             p['video_url'], p['instagram_video_url'])
        )
        product_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Images (3 per product)
        img_ids = product_image_ids[idx] if idx < len(product_image_ids) else product_image_ids[0]
        for img_idx, uid in enumerate(img_ids):
            image_url = f"https://images.unsplash.com/photo-{uid}?w=600&h=700&fit=crop"
            db.execute(
                "INSERT INTO product_images (product_id, image_path, is_main, sort_order) VALUES (?, ?, ?, ?)",
                (product_id, image_url, 1 if img_idx == 0 else 0, img_idx)
            )

        # Sizes
        if p['category_id'] == 5:  # Кроссовки
            chosen_sizes = random.sample(shoe_sizes, random.randint(4, 6))
            chosen_sizes.sort(key=lambda x: int(x))
        elif p['category_id'] == 6:  # Аксессуары
            chosen_sizes = ['ONE SIZE']
        else:
            chosen_sizes = random.sample(clothing_sizes, random.randint(3, 5))
            size_order = {s: i for i, s in enumerate(clothing_sizes)}
            chosen_sizes.sort(key=lambda x: size_order.get(x, 0))

        for sz in chosen_sizes:
            qty = random.randint(0, 15)
            db.execute(
                "INSERT INTO product_sizes (product_id, size, quantity) VALUES (?, ?, ?)",
                (product_id, sz, qty)
            )

    # ========== Site Settings ==========
    settings = [
        ('whatsapp_number', '87002259184'),
        ('instagram_account', ''),
        ('telegram_username', ''),
        ('site_name', 'BrandCode'),
        ('site_description', 'Магазин брендовой одежды'),
        ('delivery_info', 'Доставка по Казахстану 1-5 рабочих дней. Бесплатная доставка при заказе от 50 000 ₸. Доставка курьером по Алматы и Астане — 2 000 ₸. Доставка в другие города Казпочтой — 1 500 ₸.'),
        ('return_policy', 'Возврат товара возможен в течение 14 дней с момента получения. Товар должен быть в оригинальной упаковке, без следов носки. Для возврата свяжитесь с нами через WhatsApp.'),
        ('about_text', 'BrandCode — магазин оригинальной брендовой одежды и обуви в Казахстане. Мы предлагаем только 100% оригинальные товары от мировых брендов уличной моды. Работаем с 2022 года.'),
        ('show_stock_to_users', '1'),
    ]
    for key, value in settings:
        db.execute(
            "INSERT INTO site_settings (key, value) VALUES (?, ?)",
            (key, value)
        )

    # ========== Promo Banners ==========
    banners = [
        (
            'Новая коллекция SS26',
            'Весенние новинки уже в наличии',
            'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1200&h=500&fit=crop',
            '/catalog?sort=newest',
            1
        ),
        (
            'Распродажа до -40%',
            'Успей купить по лучшей цене',
            'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=1200&h=500&fit=crop',
            '/catalog?sort=price_asc&sale=1',
            2
        ),
        (
            'Кроссовки: хиты сезона',
            'Jordan, Yeezy, Triple S и другие',
            'https://images.unsplash.com/photo-1552346154-21d32810aba3?w=1200&h=500&fit=crop',
            '/catalog?category=krossovki',
            3
        ),
    ]
    for title, subtitle, image_url, link, sort_order in banners:
        db.execute(
            "INSERT INTO promo_banners (title, subtitle, image_url, link, sort_order) VALUES (?, ?, ?, ?, ?)",
            (title, subtitle, image_url, link, sort_order)
        )

    db.commit()

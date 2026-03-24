import os
import uuid
import json
from urllib.parse import quote
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, g, abort
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from database import get_db, init_db

app = Flask(__name__)
app.secret_key = 'brandcode-secret-2024'
app.config['DATABASE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'brandcode.db')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov'}


# ========== Database teardown ==========
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def get_database():
    if 'db' not in g:
        g.db = get_db()
    return g.db


# ========== Template Filters ==========
@app.template_filter('format_price')
def format_price(value):
    if value is None:
        return '0 ₸'
    value = int(value)
    formatted = '{:,}'.format(value).replace(',', ' ')
    return f'{formatted} ₸'


@app.template_filter('format_date')
def format_date(value):
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                dt = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value
    else:
        dt = value
    return dt.strftime('%d.%m.%Y %H:%M')


# ========== Helper Functions ==========
def get_site_settings():
    db = get_database()
    rows = db.execute("SELECT key, value FROM site_settings").fetchall()
    return {row['key']: row['value'] for row in rows}


def get_cart_items():
    cart = session.get('cart', [])
    if not cart:
        return [], 0

    db = get_database()
    items = []
    total = 0
    valid_cart = []

    for item in cart:
        product = db.execute(
            """SELECT p.*,
               (SELECT pi.image_path FROM product_images pi WHERE pi.product_id = p.id ORDER BY pi.is_main DESC, pi.sort_order LIMIT 1) as main_image
               FROM products p
               WHERE p.id = ? AND p.is_active = 1""",
            (item['product_id'],)
        ).fetchone()

        if product:
            size_info = db.execute(
                "SELECT * FROM product_sizes WHERE product_id = ? AND size = ?",
                (item['product_id'], item['size'])
            ).fetchone()

            quantity = min(item['quantity'], size_info['quantity'] if size_info else 0)
            if quantity > 0:
                subtotal = product['price'] * quantity
                total += subtotal
                items.append({
                    'product_id': product['id'],
                    'name': product['name'],
                    'brand': product['brand'],
                    'slug': product['slug'],
                    'price': product['price'],
                    'old_price': product['old_price'],
                    'image': product['main_image'],
                    'size': item['size'],
                    'quantity': quantity,
                    'subtotal': subtotal,
                    'max_quantity': size_info['quantity'] if size_info else 0,
                })
                valid_cart.append({'product_id': item['product_id'], 'size': item['size'], 'quantity': quantity})

    session['cart'] = valid_cart
    return items, total


def get_cart_count():
    cart = session.get('cart', [])
    return sum(item.get('quantity', 0) for item in cart)


def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


def save_upload(file, subfolder='products'):
    if file and file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        return f"/static/uploads/{subfolder}/{filename}"
    return None


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def attach_images(db, products):
    """Attach images list to each product dict"""
    result = []
    for p in products:
        d = dict(p)
        imgs = db.execute(
            "SELECT * FROM product_images WHERE product_id = ? ORDER BY is_main DESC, sort_order",
            (d['id'],)
        ).fetchall()
        d['images'] = [dict(i) for i in imgs]
        result.append(d)
    return result


# ========== Context Processor ==========
@app.context_processor
def inject_globals():
    settings = get_site_settings()
    # Count wishlist items for current session
    wishlist_count = 0
    try:
        session_id = session.get('session_id')
        if session_id:
            db = get_database()
            row = db.execute(
                "SELECT COUNT(*) FROM wishlist WHERE session_id = ?", (session_id,)
            ).fetchone()
            wishlist_count = row[0] if row else 0
    except Exception:
        pass
    return {
        'cart_count': get_cart_count(),
        'wishlist_count': wishlist_count,
        'site_settings': settings,
        'current_year': 2026,
    }


# ========================================================================
#                           PUBLIC ROUTES
# ========================================================================

@app.route('/')
def index():
    db = get_database()
    featured_products = db.execute(
        """SELECT p.*, pi.image_path as main_image
           FROM products p
           LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_main = 1
           WHERE p.is_active = 1 AND p.is_featured = 1
           ORDER BY p.created_at DESC LIMIT 8"""
    ).fetchall()

    new_products = db.execute(
        """SELECT p.*, pi.image_path as main_image
           FROM products p
           LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_main = 1
           WHERE p.is_active = 1 AND p.is_new = 1
           ORDER BY p.created_at DESC LIMIT 8"""
    ).fetchall()

    sale_products = db.execute(
        """SELECT p.*, pi.image_path as main_image
           FROM products p
           LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_main = 1
           WHERE p.is_active = 1 AND p.is_sale = 1
           ORDER BY p.created_at DESC LIMIT 8"""
    ).fetchall()

    categories = db.execute(
        "SELECT * FROM categories WHERE is_active = 1 ORDER BY sort_order"
    ).fetchall()

    banners = db.execute(
        "SELECT * FROM promo_banners WHERE is_active = 1 ORDER BY sort_order"
    ).fetchall()

    featured_products = attach_images(db, featured_products)
    new_products = attach_images(db, new_products)
    sale_products = attach_images(db, sale_products)

    return render_template('index.html',
                           featured_products=featured_products,
                           new_products=new_products,
                           sale_products=sale_products,
                           categories=categories,
                           banners=banners)


@app.route('/catalog')
def catalog():
    db = get_database()
    page = request.args.get('page', 1, type=int)
    per_page = 12

    category_slug = request.args.get('category', '')
    brand = request.args.get('brand', '')
    gender = request.args.get('gender', '')
    min_price = request.args.get('min_price', type=int) or request.args.get('price_min', type=int)
    max_price = request.args.get('max_price', type=int) or request.args.get('price_max', type=int)
    sort = request.args.get('sort', 'newest')
    q = request.args.get('q', '') or request.args.get('search', '')
    sale_only = request.args.get('sale', '') or request.args.get('on_sale', '')

    query = """SELECT p.*, pi.image_path as main_image
               FROM products p
               LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_main = 1
               LEFT JOIN categories c ON c.id = p.category_id
               WHERE p.is_active = 1"""
    count_query = """SELECT COUNT(DISTINCT p.id)
                     FROM products p
                     LEFT JOIN categories c ON c.id = p.category_id
                     WHERE p.is_active = 1"""
    params = []
    count_params = []

    if category_slug:
        query += " AND c.slug = ?"
        count_query += " AND c.slug = ?"
        params.append(category_slug)
        count_params.append(category_slug)

    if brand:
        query += " AND p.brand = ?"
        count_query += " AND p.brand = ?"
        params.append(brand)
        count_params.append(brand)

    if gender:
        query += " AND (p.gender = ? OR p.gender = 'unisex')"
        count_query += " AND (p.gender = ? OR p.gender = 'unisex')"
        params.append(gender)
        count_params.append(gender)

    if min_price:
        query += " AND p.price >= ?"
        count_query += " AND p.price >= ?"
        params.append(min_price)
        count_params.append(min_price)

    if max_price:
        query += " AND p.price <= ?"
        count_query += " AND p.price <= ?"
        params.append(max_price)
        count_params.append(max_price)

    if q:
        query += " AND (p.name LIKE ? OR p.description LIKE ? OR p.brand LIKE ?)"
        count_query += " AND (p.name LIKE ? OR p.description LIKE ? OR p.brand LIKE ?)"
        search_term = f"%{q}%"
        params.extend([search_term, search_term, search_term])
        count_params.extend([search_term, search_term, search_term])

    if sale_only:
        query += " AND p.is_sale = 1"
        count_query += " AND p.is_sale = 1"

    # Sorting
    if sort == 'price_asc':
        query += " ORDER BY p.price ASC"
    elif sort == 'price_desc':
        query += " ORDER BY p.price DESC"
    elif sort == 'popular':
        query += " ORDER BY p.views_count DESC"
    else:  # newest
        query += " ORDER BY p.created_at DESC"

    # Count
    total = db.execute(count_query, count_params).fetchone()[0]
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = min(page, total_pages)
    offset = (page - 1) * per_page

    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    products = db.execute(query, params).fetchall()
    products = attach_images(db, products)

    # Add is_out_of_stock to each product
    for p in products:
        sizes = db.execute(
            "SELECT SUM(quantity) as total_qty FROM product_sizes WHERE product_id = ?",
            (p['id'],)
        ).fetchone()
        p['is_out_of_stock'] = (sizes['total_qty'] or 0) == 0

    categories = db.execute(
        "SELECT * FROM categories WHERE is_active = 1 ORDER BY sort_order"
    ).fetchall()

    brands = db.execute(
        "SELECT name FROM brands WHERE is_active = 1 ORDER BY sort_order"
    ).fetchall()

    # Get current category object if filtering by category
    current_category = None
    if category_slug:
        current_category = db.execute(
            "SELECT * FROM categories WHERE slug = ?", (category_slug,)
        ).fetchone()

    filters = {
        'category': category_slug,
        'brand': brand,
        'gender': gender,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
        'q': q,
        'sale': sale_only,
    }

    return render_template('catalog.html',
                           products=products,
                           categories=categories,
                           brands=[b['name'] for b in brands],
                           filters=filters,
                           page=page,
                           total_pages=total_pages,
                           total=total,
                           total_count=total,
                           current_category=current_category)


@app.route('/product/<slug>')
def product_detail(slug):
    db = get_database()
    product = db.execute(
        """SELECT p.*, c.name as category_name, c.slug as category_slug
           FROM products p
           LEFT JOIN categories c ON c.id = p.category_id
           WHERE p.slug = ? AND p.is_active = 1""",
        (slug,)
    ).fetchone()

    if not product:
        abort(404)

    # Increment views
    db.execute("UPDATE products SET views_count = views_count + 1 WHERE id = ?", (product['id'],))
    db.commit()

    images = db.execute(
        "SELECT * FROM product_images WHERE product_id = ? ORDER BY sort_order",
        (product['id'],)
    ).fetchall()

    sizes = db.execute(
        "SELECT * FROM product_sizes WHERE product_id = ? ORDER BY id",
        (product['id'],)
    ).fetchall()

    related_products = db.execute(
        """SELECT p.*, pi.image_path as main_image
           FROM products p
           LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_main = 1
           WHERE p.category_id = ? AND p.id != ? AND p.is_active = 1
           ORDER BY RANDOM() LIMIT 4""",
        (product['category_id'], product['id'])
    ).fetchall()
    related_products = attach_images(db, related_products)

    # Build product dict with images attached
    product_dict = dict(product)
    product_dict['images'] = [dict(i) for i in images]
    product_dict['sizes'] = [dict(s) for s in sizes]
    product_dict['category_name'] = product['category_name']
    product_dict['category_slug'] = product['category_slug']

    # Check wishlist
    session_id = get_session_id()
    in_wishlist = db.execute(
        "SELECT id FROM wishlist WHERE session_id = ? AND product_id = ?",
        (session_id, product['id'])
    ).fetchone() is not None

    return render_template('product.html',
                           product=product_dict,
                           images=images,
                           sizes=sizes,
                           related_products=related_products,
                           in_wishlist=in_wishlist)


# ========== Cart Routes ==========

@app.route('/cart/add', methods=['POST'])
def cart_add():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Неверный формат данных'}), 400

    product_id = data.get('product_id')
    size = data.get('size')
    quantity = data.get('quantity', 1)

    if not product_id or not size:
        return jsonify({'success': False, 'message': 'Укажите товар и размер'}), 400

    db = get_database()
    product = db.execute(
        "SELECT * FROM products WHERE id = ? AND is_active = 1",
        (product_id,)
    ).fetchone()

    if not product:
        return jsonify({'success': False, 'message': 'Товар не найден'}), 404

    size_info = db.execute(
        "SELECT * FROM product_sizes WHERE product_id = ? AND size = ?",
        (product_id, size)
    ).fetchone()

    if not size_info:
        return jsonify({'success': False, 'message': 'Размер не найден'}), 404

    if size_info['quantity'] < 1:
        return jsonify({'success': False, 'message': 'Нет в наличии'}), 400

    cart = session.get('cart', [])

    # Check if already in cart
    found = False
    for item in cart:
        if item['product_id'] == product_id and item['size'] == size:
            new_qty = item['quantity'] + quantity
            if new_qty > size_info['quantity']:
                return jsonify({'success': False, 'message': f'Доступно только {size_info["quantity"]} шт.'}), 400
            item['quantity'] = new_qty
            found = True
            break

    if not found:
        if quantity > size_info['quantity']:
            return jsonify({'success': False, 'message': f'Доступно только {size_info["quantity"]} шт.'}), 400
        cart.append({
            'product_id': product_id,
            'size': size,
            'quantity': quantity
        })

    session['cart'] = cart
    return jsonify({
        'success': True,
        'cart_count': get_cart_count(),
        'message': 'Товар добавлен в корзину'
    })


@app.route('/cart/update', methods=['POST'])
def cart_update():
    data = request.get_json()
    if not data:
        return jsonify({'success': False}), 400

    product_id = data.get('product_id') or data.get('index')
    size = data.get('size', '')
    quantity = data.get('quantity', 0)
    cart = session.get('cart', [])

    # Find item by product_id + size, or by index
    idx = None
    if size:
        for i, item in enumerate(cart):
            if item['product_id'] == product_id and item['size'] == size:
                idx = i
                break
    elif isinstance(product_id, int) and product_id < len(cart):
        idx = product_id

    if idx is None:
        return jsonify({'success': False, 'message': 'Товар не найден в корзине'}), 400

    if quantity <= 0:
        cart.pop(idx)
    else:
        db = get_database()
        item = cart[idx]
        size_info = db.execute(
            "SELECT * FROM product_sizes WHERE product_id = ? AND size = ?",
            (item['product_id'], item['size'])
        ).fetchone()
        max_qty = size_info['quantity'] if size_info else 0
        cart[idx]['quantity'] = min(quantity, max_qty)

    session['cart'] = cart
    _, total = get_cart_items()
    return jsonify({
        'success': True,
        'cart_count': get_cart_count(),
        'total': total
    })


@app.route('/cart/remove', methods=['POST'])
def cart_remove():
    data = request.get_json()
    if not data:
        return jsonify({'success': False}), 400

    product_id = data.get('product_id') or data.get('index')
    size = data.get('size', '')
    cart = session.get('cart', [])

    # Find item by product_id + size
    idx = None
    if size:
        for i, item in enumerate(cart):
            if item['product_id'] == product_id and item['size'] == size:
                idx = i
                break
    elif isinstance(product_id, int) and product_id < len(cart):
        idx = product_id

    if idx is None:
        return jsonify({'success': False, 'message': 'Товар не найден'}), 400

    cart.pop(idx)
    session['cart'] = cart
    _, total = get_cart_items()
    return jsonify({
        'success': True,
        'cart_count': get_cart_count(),
        'total': total
    })


@app.route('/cart')
def cart():
    items, total = get_cart_items()
    return render_template('cart.html', items=items, total=total)


@app.route('/checkout', methods=['POST'])
def checkout():
    items, total = get_cart_items()
    if not items:
        flash('Корзина пуста', 'error')
        return redirect(url_for('cart'))

    if request.is_json:
        data = request.get_json()
        customer_name = data.get('customer_name', '').strip()
        customer_phone = data.get('customer_phone', '').strip()
        customer_city = data.get('customer_city', '').strip()
        delivery_method = data.get('delivery_method', 'pickup')
    else:
        data = None
        customer_name = request.form.get('customer_name', '').strip()
        customer_phone = request.form.get('customer_phone', '').strip()
        customer_city = request.form.get('customer_city', '').strip()
        delivery_method = request.form.get('delivery_method', '').strip()

    if not customer_name or not customer_phone:
        flash('Заполните имя и номер телефона', 'error')
        return redirect(url_for('cart'))

    db = get_database()
    items_data = []
    for item in items:
        items_data.append({
            'product_id': item['product_id'],
            'name': item['name'],
            'size': item['size'],
            'quantity': item['quantity'],
            'price': item['price'],
            'subtotal': item['subtotal'],
        })

    db.execute(
        """INSERT INTO orders (customer_name, customer_phone, customer_city,
           delivery_method, items_json, total_amount)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (customer_name, customer_phone, customer_city,
         delivery_method, json.dumps(items_data, ensure_ascii=False), total)
    )
    order_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Decrease stock
    for item in items:
        db.execute(
            "UPDATE product_sizes SET quantity = quantity - ? WHERE product_id = ? AND size = ?",
            (item['quantity'], item['product_id'], item['size'])
        )

    db.commit()

    # Build WhatsApp message
    settings = get_site_settings()
    whatsapp_number = settings.get('whatsapp_number', '87002259184')
    # Convert 8700... to 7700... for wa.me
    if whatsapp_number.startswith('8'):
        wa_number = '7' + whatsapp_number[1:]
    else:
        wa_number = whatsapp_number

    message_lines = [
        f"🛒 *Новый заказ #{order_id}*",
        f"",
        f"👤 *Клиент:* {customer_name}",
        f"📱 *Телефон:* {customer_phone}",
    ]
    if customer_city:
        message_lines.append(f"🏙 *Город:* {customer_city}")
    if delivery_method:
        message_lines.append(f"🚚 *Доставка:* {delivery_method}")

    message_lines.append("")
    message_lines.append("*Товары:*")

    for item in items:
        price_fmt = '{:,}'.format(item['price']).replace(',', ' ')
        subtotal_fmt = '{:,}'.format(item['subtotal']).replace(',', ' ')
        message_lines.append(
            f"• {item['name']} | Размер: {item['size']} | {item['quantity']} шт. | {subtotal_fmt} ₸"
        )

    total_fmt = '{:,}'.format(total).replace(',', ' ')
    message_lines.append("")
    message_lines.append(f"💰 *Итого: {total_fmt} ₸*")

    message_text = '\n'.join(message_lines)
    whatsapp_url = f"https://wa.me/{wa_number}?text={quote(message_text)}"

    # Clear cart
    session['cart'] = []

    if request.headers.get('Content-Type') == 'application/json' or request.is_json:
        return jsonify({
            'success': True,
            'order_id': order_id,
            'whatsapp_url': whatsapp_url,
            'message': 'Заказ оформлен!'
        })

    flash('Заказ успешно оформлен!', 'success')
    return redirect(whatsapp_url)


# ========== Wishlist Routes ==========

@app.route('/wishlist')
def wishlist():
    session_id = get_session_id()
    db = get_database()
    products = db.execute(
        """SELECT p.*, pi.image_path as main_image
           FROM wishlist w
           JOIN products p ON p.id = w.product_id
           LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_main = 1
           WHERE w.session_id = ? AND p.is_active = 1
           ORDER BY w.created_at DESC""",
        (session_id,)
    ).fetchall()
    products = attach_images(db, products)
    return render_template('wishlist.html', products=products)


@app.route('/wishlist/toggle', methods=['POST'])
def wishlist_toggle():
    data = request.get_json()
    if not data or 'product_id' not in data:
        return jsonify({'success': False}), 400

    product_id = data['product_id']
    session_id = get_session_id()
    db = get_database()

    existing = db.execute(
        "SELECT id FROM wishlist WHERE session_id = ? AND product_id = ?",
        (session_id, product_id)
    ).fetchone()

    if existing:
        db.execute("DELETE FROM wishlist WHERE id = ?", (existing['id'],))
        db.commit()
        return jsonify({'success': True, 'status': 'removed'})
    else:
        db.execute(
            "INSERT INTO wishlist (session_id, product_id) VALUES (?, ?)",
            (session_id, product_id)
        )
        db.commit()
        return jsonify({'success': True, 'status': 'added'})


# ========== Search ==========

@app.route('/search')
def search():
    q = request.args.get('q', '')
    if not q:
        return redirect(url_for('catalog'))
    return redirect(url_for('catalog', q=q))


# ========== Info Pages ==========

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/delivery')
def delivery():
    return render_template('delivery.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/payment')
def payment():
    return redirect(url_for('delivery'))


@app.route('/returns')
def returns():
    return redirect(url_for('delivery'))


# ========================================================================
#                           ADMIN ROUTES
# ========================================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        db = get_database()
        user = db.execute(
            "SELECT * FROM admin_users WHERE username = ?",
            (username,)
        ).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Добро пожаловать!', 'success')
            return redirect(url_for('admin_dashboard'))

        flash('Неверный логин или пароль', 'error')

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_database()
    stats = {
        'products_count': db.execute("SELECT COUNT(*) FROM products").fetchone()[0],
        'active_products': db.execute("SELECT COUNT(*) FROM products WHERE is_active = 1").fetchone()[0],
        'orders_count': db.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        'new_orders': db.execute("SELECT COUNT(*) FROM orders WHERE status = 'new'").fetchone()[0],
        'total_revenue': db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders").fetchone()[0],
        'categories_count': db.execute("SELECT COUNT(*) FROM categories").fetchone()[0],
    }
    recent_orders = db.execute(
        "SELECT * FROM orders ORDER BY created_at DESC LIMIT 10"
    ).fetchall()
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)


# ========== Admin Products ==========

@app.route('/admin/products')
@admin_required
def admin_products():
    db = get_database()
    q = request.args.get('q', '')
    category_id = request.args.get('category_id', type=int)

    query = """SELECT p.*, c.name as category_name, pi.image_path as main_image,
               COALESCE((SELECT SUM(ps.quantity) FROM product_sizes ps WHERE ps.product_id = p.id), 0) as total_stock
               FROM products p
               LEFT JOIN categories c ON c.id = p.category_id
               LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_main = 1
               WHERE 1=1"""
    params = []

    if q:
        query += " AND (p.name LIKE ? OR p.brand LIKE ?)"
        params.extend([f'%{q}%', f'%{q}%'])

    if category_id:
        query += " AND p.category_id = ?"
        params.append(category_id)

    query += " ORDER BY p.created_at DESC"
    products = db.execute(query, params).fetchall()
    categories = db.execute("SELECT * FROM categories ORDER BY sort_order").fetchall()
    return render_template('admin/products.html', products=products, categories=categories, q=q)


@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_product_add():
    db = get_database()
    categories = db.execute("SELECT * FROM categories WHERE is_active = 1 ORDER BY sort_order").fetchall()
    brands = db.execute("SELECT * FROM brands WHERE is_active = 1 ORDER BY sort_order").fetchall()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        slug = request.form.get('slug', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0, type=int)
        old_price = request.form.get('old_price', type=int)
        category_id = request.form.get('category_id', type=int)
        brand = request.form.get('brand', '').strip()
        gender = request.form.get('gender', 'unisex')
        is_featured = 1 if request.form.get('is_featured') else 0
        is_new = 1 if request.form.get('is_new') else 0
        is_sale = 1 if request.form.get('is_sale') else 0
        video_url = request.form.get('video_url', '').strip() or None
        instagram_video_url = request.form.get('instagram_video_url', '').strip() or None

        if not name or not slug or not price:
            flash('Заполните обязательные поля', 'error')
            return render_template('admin/product_form.html', categories=categories, brands=brands, product=None)

        if not old_price:
            old_price = None

        try:
            db.execute(
                """INSERT INTO products
                (name, slug, description, price, old_price, category_id, brand, gender,
                 is_featured, is_new, is_sale, video_url, instagram_video_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, slug, description, price, old_price, category_id, brand, gender,
                 is_featured, is_new, is_sale, video_url, instagram_video_url)
            )
            product_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

            # Handle image uploads
            images = request.files.getlist('images')
            for idx, img in enumerate(images):
                if img and img.filename and allowed_image(img.filename):
                    image_path = save_upload(img, 'products')
                    if image_path:
                        db.execute(
                            "INSERT INTO product_images (product_id, image_path, is_main, sort_order) VALUES (?, ?, ?, ?)",
                            (product_id, image_path, 1 if idx == 0 else 0, idx)
                        )

            # Handle image URLs
            image_urls = request.form.get('image_urls', '').strip()
            if image_urls:
                existing_count = len([i for i in images if i and i.filename])
                for idx, url in enumerate(image_urls.split('\n')):
                    url = url.strip()
                    if url:
                        db.execute(
                            "INSERT INTO product_images (product_id, image_path, is_main, sort_order) VALUES (?, ?, ?, ?)",
                            (product_id, url, 1 if idx == 0 and existing_count == 0 else 0, existing_count + idx)
                        )

            # Handle video upload
            video = request.files.get('video_file')
            if video and video.filename and allowed_video(video.filename):
                video_path = save_upload(video, 'videos')
                if video_path:
                    db.execute("UPDATE products SET video_url = ? WHERE id = ?", (video_path, product_id))

            # Handle sizes
            size_names = request.form.getlist('size_name[]')
            size_qtys = request.form.getlist('size_qty[]')
            for sname, sqty in zip(size_names, size_qtys):
                sname = sname.strip()
                if sname:
                    db.execute(
                        "INSERT INTO product_sizes (product_id, size, quantity) VALUES (?, ?, ?)",
                        (product_id, sname, int(sqty) if sqty else 0)
                    )

            db.commit()
            flash('Товар добавлен', 'success')
            return redirect(url_for('admin_products'))
        except Exception as e:
            db.rollback()
            flash(f'Ошибка: {str(e)}', 'error')

    return render_template('admin/product_form.html', categories=categories, brands=brands, product=None)


@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_product_edit(id):
    db = get_database()
    product = db.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    if not product:
        abort(404)

    categories = db.execute("SELECT * FROM categories WHERE is_active = 1 ORDER BY sort_order").fetchall()
    brands = db.execute("SELECT * FROM brands WHERE is_active = 1 ORDER BY sort_order").fetchall()
    images = db.execute("SELECT * FROM product_images WHERE product_id = ? ORDER BY sort_order", (id,)).fetchall()
    sizes = db.execute("SELECT * FROM product_sizes WHERE product_id = ? ORDER BY id", (id,)).fetchall()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        slug = request.form.get('slug', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0, type=int)
        old_price = request.form.get('old_price', type=int)
        category_id = request.form.get('category_id', type=int)
        brand = request.form.get('brand', '').strip()
        gender = request.form.get('gender', 'unisex')
        is_active = 1 if request.form.get('is_active') else 0
        is_featured = 1 if request.form.get('is_featured') else 0
        is_new = 1 if request.form.get('is_new') else 0
        is_sale = 1 if request.form.get('is_sale') else 0
        video_url = request.form.get('video_url', '').strip() or None
        instagram_video_url = request.form.get('instagram_video_url', '').strip() or None

        if not old_price:
            old_price = None

        try:
            db.execute(
                """UPDATE products SET
                name=?, slug=?, description=?, price=?, old_price=?, category_id=?, brand=?,
                gender=?, is_active=?, is_featured=?, is_new=?, is_sale=?, video_url=?, instagram_video_url=?
                WHERE id=?""",
                (name, slug, description, price, old_price, category_id, brand, gender,
                 is_active, is_featured, is_new, is_sale, video_url, instagram_video_url, id)
            )

            # Handle new image uploads
            new_images = request.files.getlist('images')
            existing_max = db.execute(
                "SELECT COALESCE(MAX(sort_order), -1) FROM product_images WHERE product_id = ?", (id,)
            ).fetchone()[0]

            for idx, img in enumerate(new_images):
                if img and img.filename and allowed_image(img.filename):
                    image_path = save_upload(img, 'products')
                    if image_path:
                        db.execute(
                            "INSERT INTO product_images (product_id, image_path, is_main, sort_order) VALUES (?, ?, ?, ?)",
                            (id, image_path, 0, existing_max + 1 + idx)
                        )

            # Handle new image URLs
            image_urls = request.form.get('image_urls', '').strip()
            if image_urls:
                existing_max2 = db.execute(
                    "SELECT COALESCE(MAX(sort_order), -1) FROM product_images WHERE product_id = ?", (id,)
                ).fetchone()[0]
                for idx, url in enumerate(image_urls.split('\n')):
                    url = url.strip()
                    if url:
                        db.execute(
                            "INSERT INTO product_images (product_id, image_path, is_main, sort_order) VALUES (?, ?, ?, ?)",
                            (id, url, 0, existing_max2 + 1 + idx)
                        )

            # Delete selected images
            delete_images = request.form.getlist('delete_images')
            for img_id in delete_images:
                db.execute("DELETE FROM product_images WHERE id = ? AND product_id = ?", (img_id, id))

            # Set main image
            main_image_id = request.form.get('main_image_id', type=int)
            if main_image_id:
                db.execute("UPDATE product_images SET is_main = 0 WHERE product_id = ?", (id,))
                db.execute("UPDATE product_images SET is_main = 1 WHERE id = ? AND product_id = ?", (main_image_id, id))

            # Handle video upload
            video = request.files.get('video_file')
            if video and video.filename and allowed_video(video.filename):
                video_path = save_upload(video, 'videos')
                if video_path:
                    db.execute("UPDATE products SET video_url = ? WHERE id = ?", (video_path, id))

            # Update sizes
            size_names = request.form.getlist('size_name[]')
            size_qtys = request.form.getlist('size_qty[]')
            if size_names:
                db.execute("DELETE FROM product_sizes WHERE product_id = ?", (id,))
                for sname, sqty in zip(size_names, size_qtys):
                    sname = sname.strip()
                    if sname:
                        db.execute(
                            "INSERT INTO product_sizes (product_id, size, quantity) VALUES (?, ?, ?)",
                            (id, sname, int(sqty) if sqty else 0)
                        )

            db.commit()
            flash('Товар обновлён', 'success')
            return redirect(url_for('admin_products'))
        except Exception as e:
            db.rollback()
            flash(f'Ошибка: {str(e)}', 'error')

    # Format sizes for textarea
    sizes_text = '\n'.join([f"{s['size']}:{s['quantity']}" for s in sizes])

    return render_template('admin/product_form.html',
                           categories=categories,
                           brands=brands,
                           product=product,
                           images=images,
                           sizes=sizes,
                           sizes_text=sizes_text)


@app.route('/admin/products/delete/<int:id>', methods=['POST'])
@admin_required
def admin_product_delete(id):
    db = get_database()
    db.execute("DELETE FROM product_images WHERE product_id = ?", (id,))
    db.execute("DELETE FROM product_sizes WHERE product_id = ?", (id,))
    db.execute("DELETE FROM wishlist WHERE product_id = ?", (id,))
    db.execute("DELETE FROM products WHERE id = ?", (id,))
    db.commit()
    flash('Товар удалён', 'success')
    return redirect(url_for('admin_products'))


@app.route('/admin/products/toggle/<int:id>', methods=['POST'])
@admin_required
def admin_product_toggle(id):
    db = get_database()
    db.execute("UPDATE products SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?", (id,))
    db.commit()
    flash('Статус товара изменён', 'success')
    return redirect(url_for('admin_products'))


@app.route('/admin/products/toggle-featured/<int:id>', methods=['POST'])
@admin_required
def admin_product_toggle_featured(id):
    db = get_database()
    db.execute("UPDATE products SET is_featured = CASE WHEN is_featured = 1 THEN 0 ELSE 1 END WHERE id = ?", (id,))
    db.commit()
    flash('Статус «Рекомендуемый» изменён', 'success')
    return redirect(url_for('admin_products'))


# ========== Admin Categories ==========

@app.route('/admin/categories')
@admin_required
def admin_categories():
    db = get_database()
    categories = db.execute(
        """SELECT c.*, COUNT(p.id) as products_count
           FROM categories c
           LEFT JOIN products p ON p.category_id = c.id
           GROUP BY c.id
           ORDER BY c.sort_order"""
    ).fetchall()
    return render_template('admin/categories.html', categories=categories)


@app.route('/admin/categories/add', methods=['POST'])
@admin_required
def admin_category_add():
    name = request.form.get('name', '').strip()
    slug = request.form.get('slug', '').strip()
    icon = request.form.get('icon', '').strip()
    image_url = request.form.get('image_url', '').strip()
    sort_order = request.form.get('sort_order', 0, type=int)

    if not name or not slug:
        flash('Заполните название и slug', 'error')
        return redirect(url_for('admin_categories'))

    db = get_database()
    try:
        db.execute(
            "INSERT INTO categories (name, slug, icon, image_url, sort_order) VALUES (?, ?, ?, ?, ?)",
            (name, slug, icon, image_url, sort_order)
        )
        db.commit()
        flash('Категория добавлена', 'success')
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
    return redirect(url_for('admin_categories'))


@app.route('/admin/categories/edit/<int:id>', methods=['POST'])
@admin_required
def admin_category_edit(id):
    name = request.form.get('name', '').strip()
    slug = request.form.get('slug', '').strip()
    icon = request.form.get('icon', '').strip()
    image_url = request.form.get('image_url', '').strip()
    sort_order = request.form.get('sort_order', 0, type=int)
    is_active = 1 if request.form.get('is_active') else 0

    db = get_database()
    try:
        db.execute(
            "UPDATE categories SET name=?, slug=?, icon=?, image_url=?, sort_order=?, is_active=? WHERE id=?",
            (name, slug, icon, image_url, sort_order, is_active, id)
        )
        db.commit()
        flash('Категория обновлена', 'success')
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
    return redirect(url_for('admin_categories'))


@app.route('/admin/categories/delete/<int:id>', methods=['POST'])
@admin_required
def admin_category_delete(id):
    db = get_database()
    product_count = db.execute(
        "SELECT COUNT(*) FROM products WHERE category_id = ?", (id,)
    ).fetchone()[0]
    if product_count > 0:
        flash(f'Невозможно удалить: в категории {product_count} товаров', 'error')
    else:
        db.execute("DELETE FROM categories WHERE id = ?", (id,))
        db.commit()
        flash('Категория удалена', 'success')
    return redirect(url_for('admin_categories'))


# ========== Admin Orders ==========

@app.route('/admin/orders')
@admin_required
def admin_orders():
    db = get_database()
    status_filter = request.args.get('status', '')
    query = "SELECT * FROM orders"
    params = []
    if status_filter:
        query += " WHERE status = ?"
        params.append(status_filter)
    query += " ORDER BY created_at DESC"
    orders = db.execute(query, params).fetchall()

    # Parse items_json for display
    orders_list = []
    for order in orders:
        o = dict(order)
        try:
            o['order_items'] = json.loads(o['items_json'])
        except (json.JSONDecodeError, TypeError):
            o['order_items'] = []
        orders_list.append(o)

    return render_template('admin/orders.html', orders=orders_list, status_filter=status_filter)


@app.route('/admin/orders/status/<int:id>', methods=['POST'])
@admin_required
def admin_order_status(id):
    status = request.form.get('status', 'new')
    db = get_database()
    db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, id))
    db.commit()
    flash('Статус заказа обновлён', 'success')
    return redirect(url_for('admin_orders'))


# ========== Admin Settings ==========

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    db = get_database()
    if request.method == 'POST':
        keys = ['whatsapp_number', 'instagram_account', 'telegram_username',
                'site_name', 'site_description', 'delivery_info', 'return_policy', 'about_text']
        for key in keys:
            value = request.form.get(key, '').strip()
            existing = db.execute("SELECT id FROM site_settings WHERE key = ?", (key,)).fetchone()
            if existing:
                db.execute("UPDATE site_settings SET value = ? WHERE key = ?", (value, key))
            else:
                db.execute("INSERT INTO site_settings (key, value) VALUES (?, ?)", (key, value))
        # Checkbox fields (value is '1' if checked, '0' if not)
        for ckey in ['show_stock_to_users']:
            cval = '1' if request.form.get(ckey) else '0'
            existing = db.execute("SELECT id FROM site_settings WHERE key = ?", (ckey,)).fetchone()
            if existing:
                db.execute("UPDATE site_settings SET value = ? WHERE key = ?", (cval, ckey))
            else:
                db.execute("INSERT INTO site_settings (key, value) VALUES (?, ?)", (ckey, cval))
        db.commit()
        flash('Настройки сохранены', 'success')
        return redirect(url_for('admin_settings'))

    settings = get_site_settings()
    return render_template('admin/settings.html', settings=settings)


# ========== Admin Banners ==========

@app.route('/admin/banners')
@admin_required
def admin_banners():
    db = get_database()
    banners = db.execute("SELECT * FROM promo_banners ORDER BY sort_order").fetchall()
    return render_template('admin/banners.html', banners=banners)


@app.route('/admin/banners/add', methods=['POST'])
@admin_required
def admin_banner_add():
    title = request.form.get('title', '').strip()
    subtitle = request.form.get('subtitle', '').strip()
    link = request.form.get('link', '').strip()
    sort_order = request.form.get('sort_order', 0, type=int)
    is_active = 1 if request.form.get('is_active') else 0

    image_url = request.form.get('image_url', '').strip()
    image_file = request.files.get('image_file')
    if image_file and image_file.filename and allowed_image(image_file.filename):
        image_url = save_upload(image_file, 'banners')

    db = get_database()
    db.execute(
        "INSERT INTO promo_banners (title, subtitle, image_url, link, is_active, sort_order) VALUES (?, ?, ?, ?, ?, ?)",
        (title, subtitle, image_url, link, is_active, sort_order)
    )
    db.commit()
    flash('Баннер добавлен', 'success')
    return redirect(url_for('admin_banners'))


@app.route('/admin/banners/edit/<int:id>', methods=['POST'])
@admin_required
def admin_banner_edit(id):
    title = request.form.get('title', '').strip()
    subtitle = request.form.get('subtitle', '').strip()
    link = request.form.get('link', '').strip()
    sort_order = request.form.get('sort_order', 0, type=int)
    is_active = 1 if request.form.get('is_active') else 0

    image_url = request.form.get('image_url', '').strip()
    image_file = request.files.get('image_file')
    if image_file and image_file.filename and allowed_image(image_file.filename):
        image_url = save_upload(image_file, 'banners')

    db = get_database()
    if image_url:
        db.execute(
            "UPDATE promo_banners SET title=?, subtitle=?, image_url=?, link=?, is_active=?, sort_order=? WHERE id=?",
            (title, subtitle, image_url, link, is_active, sort_order, id)
        )
    else:
        db.execute(
            "UPDATE promo_banners SET title=?, subtitle=?, link=?, is_active=?, sort_order=? WHERE id=?",
            (title, subtitle, link, is_active, sort_order, id)
        )
    db.commit()
    flash('Баннер обновлён', 'success')
    return redirect(url_for('admin_banners'))


@app.route('/admin/banners/delete/<int:id>', methods=['POST'])
@admin_required
def admin_banner_delete(id):
    db = get_database()
    db.execute("DELETE FROM promo_banners WHERE id = ?", (id,))
    db.commit()
    flash('Баннер удалён', 'success')
    return redirect(url_for('admin_banners'))


# ========== Admin Brands ==========

@app.route('/admin/brands')
@admin_required
def admin_brands():
    db = get_database()
    brands = db.execute(
        """SELECT b.*, (SELECT COUNT(*) FROM products p WHERE p.brand = b.name) as products_count
           FROM brands b ORDER BY b.sort_order"""
    ).fetchall()
    return render_template('admin/brands.html', brands=brands)


@app.route('/admin/brands/add', methods=['POST'])
@admin_required
def admin_brand_add():
    name = request.form.get('name', '').strip()
    logo_url = request.form.get('logo_url', '').strip() or None
    sort_order = request.form.get('sort_order', 0, type=int)

    if not name:
        flash('Введите название бренда', 'error')
        return redirect(url_for('admin_brands'))

    db = get_database()
    try:
        db.execute(
            "INSERT INTO brands (name, logo_url, sort_order) VALUES (?, ?, ?)",
            (name, logo_url, sort_order)
        )
        db.commit()
        flash('Бренд добавлен', 'success')
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
    return redirect(url_for('admin_brands'))


@app.route('/admin/brands/edit/<int:id>', methods=['POST'])
@admin_required
def admin_brand_edit(id):
    name = request.form.get('name', '').strip()
    logo_url = request.form.get('logo_url', '').strip() or None
    sort_order = request.form.get('sort_order', 0, type=int)
    is_active = 1 if request.form.get('is_active') else 0

    db = get_database()
    try:
        db.execute(
            "UPDATE brands SET name=?, logo_url=?, sort_order=?, is_active=? WHERE id=?",
            (name, logo_url, sort_order, is_active, id)
        )
        db.commit()
        flash('Бренд обновлён', 'success')
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
    return redirect(url_for('admin_brands'))


@app.route('/admin/brands/delete/<int:id>', methods=['POST'])
@admin_required
def admin_brand_delete(id):
    db = get_database()
    brand = db.execute("SELECT name FROM brands WHERE id = ?", (id,)).fetchone()
    if brand:
        product_count = db.execute(
            "SELECT COUNT(*) FROM products WHERE brand = ?", (brand['name'],)
        ).fetchone()[0]
        if product_count > 0:
            flash(f'Невозможно удалить: у бренда {product_count} товаров', 'error')
        else:
            db.execute("DELETE FROM brands WHERE id = ?", (id,))
            db.commit()
            flash('Бренд удалён', 'success')
    return redirect(url_for('admin_brands'))


# ========== Error Handlers ==========

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', content_override='<div class="min-h-screen flex items-center justify-center"><div class="text-center"><h1 class="text-8xl font-bold text-[#d4a853]">404</h1><p class="text-xl text-gray-400 mt-4">Страница не найдена</p><a href="/" class="inline-block mt-6 px-6 py-3 bg-[#d4a853] text-black rounded-lg font-medium hover:bg-[#c8a04a]">На главную</a></div></div>'), 404


@app.errorhandler(500)
def internal_error(e):
    return '<html><body style="background:#0a0a0a;color:white;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif"><div style="text-align:center"><h1 style="font-size:4rem;color:#d4a853">500</h1><p>Внутренняя ошибка сервера</p><a href="/" style="color:#d4a853">На главную</a></div></body></html>', 500


# ========================================================================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)

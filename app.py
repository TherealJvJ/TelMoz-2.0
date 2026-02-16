import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Admin, Category, Product

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'telmoz-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///telmoz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração WhatsApp - altere para o número da empresa
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '+258847749499')

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Por favor, faça login para aceder à área administrativa.'


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


@app.context_processor
def inject_year():
    return {
        'current_year': datetime.now().year,
        'whatsapp_number': WHATSAPP_NUMBER.replace('+', '').replace(' ', '')
    }


# ============ ROTAS PÚBLICAS (sem login) ============

@app.route('/')
def index():
    """Página inicial com todos os produtos"""
    categories = Category.query.all()
    
    # Filtros de pesquisa
    search_query = request.args.get('search', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Query base
    query = Product.query
    
    # Filtro por nome
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    
    # Filtro por preço mínimo
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    # Filtro por preço máximo
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    products = query.all()
    
    return render_template('index.html', 
                         categories=categories, 
                         products=products,
                         search_query=search_query,
                         min_price=min_price,
                         max_price=max_price)


@app.route('/categoria/<int:category_id>')
def category_products(category_id):
    """Produtos por categoria"""
    category = Category.query.get_or_404(category_id)
    
    # Filtros de pesquisa
    search_query = request.args.get('search', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Query base com categoria
    query = Product.query.filter_by(category_id=category_id)
    
    # Filtro por nome
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    
    # Filtro por preço mínimo
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    # Filtro por preço máximo
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    products = query.all()
    categories = Category.query.all()
    
    return render_template('index.html', 
                         categories=categories, 
                         products=products, 
                         active_category=category,
                         search_query=search_query,
                         min_price=min_price,
                         max_price=max_price)


def get_whatsapp_url(product):
    """Gera URL do WhatsApp com mensagem do produto"""
    price_display = product.final_price if product.discount_percent > 0 else product.price
    price_text = f"MT {price_display:.2f}"
    if product.discount_percent > 0:
        price_text += f" (desconto de {product.discount_percent:.0f}%)"
    message = product.whatsapp_message or f"Olá! Gostaria de encomendar: *{product.name}* - {price_text}"
    # Codifica a mensagem para URL
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_message}"


@app.template_global()
def whatsapp_link(product):
    return get_whatsapp_url(product)


# ============ ROTAS ADMIN (com login) ============

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Login do administrador"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin)
            flash('Login efetuado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Utilizador ou palavra-passe incorretos.', 'error')
    
    return render_template('admin/login.html')


@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Esqueci a senha - solicitar reset"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        admin = Admin.query.filter_by(email=email).first()
        
        if admin:
            token = admin.generate_reset_token()
            db.session.commit()
            
            # Em produção, aqui enviaria email com o link
            reset_url = url_for('reset_password', token=token, _external=True)
            flash(f'Link de recuperação gerado! (Em produção, será enviado por email)\n{reset_url}', 'success')
            return redirect(url_for('admin_login'))
        else:
            flash('Email não encontrado.', 'error')
    
    return render_template('admin/forgot_password.html')


@app.route('/admin/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset de senha com token"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    admin = Admin.query.filter_by(reset_token=token).first()
    
    if not admin or not admin.reset_token_expires or admin.reset_token_expires < datetime.utcnow():
        flash('Token inválido ou expirado.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if password != confirm:
            flash('As senhas não coincidem.', 'error')
        elif len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
        else:
            admin.set_password(password)
            admin.reset_token = None
            admin.reset_token_expires = None
            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('admin_login'))
    
    return render_template('admin/reset_password.html', token=token)


@app.route('/admin/create-admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    """Criar novo administrador (requer login)"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('Todos os campos são obrigatórios.', 'error')
        elif password != confirm:
            flash('As senhas não coincidem.', 'error')
        elif len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
        elif Admin.query.filter_by(username=username).first():
            flash('Nome de utilizador já existe.', 'error')
        elif Admin.query.filter_by(email=email).first():
            flash('Email já está em uso.', 'error')
        else:
            admin = Admin(username=username, email=email)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            flash(f'Administrador "{username}" criado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/create_admin.html')


@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Sessão terminada.', 'success')
    return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin_dashboard():
    """Painel administrativo"""
    categories = Category.query.all()
    products = Product.query.all()
    return render_template('admin/dashboard.html', categories=categories, products=products)


# ============ CRUD CATEGORIAS ============

@app.route('/admin/categoria/adicionar', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            category = Category(name=name)
            db.session.add(category)
            db.session.commit()
            flash(f'Categoria "{name}" adicionada com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Nome da categoria é obrigatório.', 'error')
    return render_template('admin/category_form.html', category=None)


@app.route('/admin/categoria/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            category.name = name
            db.session.commit()
            flash('Categoria atualizada com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Nome da categoria é obrigatório.', 'error')
    return render_template('admin/category_form.html', category=category)


@app.route('/admin/categoria/<int:id>/eliminar', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    if category.products:
        flash('Não é possível eliminar categoria com produtos. Elimine os produtos primeiro.', 'error')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Categoria eliminada com sucesso!', 'success')
    return redirect(url_for('admin_dashboard'))


# ============ CRUD PRODUTOS ============

@app.route('/admin/produto/adicionar', methods=['GET', 'POST'])
@login_required
def add_product():
    categories = Category.query.all()
    if not categories:
        flash('Crie uma categoria primeiro.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        discount_percent = request.form.get('discount_percent', 0)
        category_id = request.form.get('category_id')
        image_url = request.form.get('image_url')
        whatsapp_message = request.form.get('whatsapp_message')
        
        if name and price and category_id:
            quantity = request.form.get('quantity', 0)
            product = Product(
                name=name,
                description=description,
                price=float(price),
                discount_percent=float(discount_percent) if discount_percent else 0.0,
                quantity=int(quantity) if quantity else 0,
                category_id=int(category_id),
                image_url=image_url or None,
                whatsapp_message=whatsapp_message or None
            )
            db.session.add(product)
            db.session.commit()
            flash(f'Produto "{name}" adicionado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Nome, preço e categoria são obrigatórios.', 'error')
    
    return render_template('admin/product_form.html', product=None, categories=categories)


@app.route('/admin/produto/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        discount_percent = request.form.get('discount_percent', 0)
        category_id = request.form.get('category_id')
        image_url = request.form.get('image_url')
        whatsapp_message = request.form.get('whatsapp_message')
        
        if name and price and category_id:
            quantity = request.form.get('quantity', 0)
            product.name = name
            product.description = description
            product.price = float(price)
            product.discount_percent = float(discount_percent) if discount_percent else 0.0
            product.quantity = int(quantity) if quantity else 0
            product.category_id = int(category_id)
            product.image_url = image_url or None
            product.whatsapp_message = whatsapp_message or None
            db.session.commit()
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Nome, preço e categoria são obrigatórios.', 'error')
    
    return render_template('admin/product_form.html', product=product, categories=categories)


@app.route('/admin/produto/<int:id>/quantidade', methods=['POST'])
@login_required
def update_product_quantity(id):
    """Atualiza a quantidade do produto (ex: após uma compra realizada)"""
    product = Product.query.get_or_404(id)
    new_quantity = request.form.get('quantity')
    if new_quantity is not None:
        try:
            product.quantity = int(new_quantity)
            db.session.commit()
            flash(f'Quantidade de "{product.name}" atualizada para {product.quantity}.', 'success')
        except ValueError:
            flash('Quantidade inválida.', 'error')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/produto/<int:id>/eliminar', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produto eliminado com sucesso!', 'success')
    return redirect(url_for('admin_dashboard'))


# ============ INICIALIZAÇÃO ============

def migrate_add_quantity():
    """Adiciona coluna quantity se não existir (para bases de dados existentes)"""
    with app.app_context():
        from sqlalchemy import text
        try:
            db.session.execute(text("ALTER TABLE products ADD COLUMN quantity INTEGER DEFAULT 0 NOT NULL"))
            db.session.commit()
        except Exception:
            db.session.rollback()

def migrate_add_discount():
    """Adiciona coluna discount_percent se não existir (para bases de dados existentes)"""
    with app.app_context():
        from sqlalchemy import text
        try:
            db.session.execute(text("ALTER TABLE products ADD COLUMN discount_percent FLOAT DEFAULT 0.0 NOT NULL"))
            db.session.commit()
        except Exception:
            db.session.rollback()

def migrate_add_reset_fields():
    """Adiciona campos de reset de senha se não existirem"""
    with app.app_context():
        from sqlalchemy import text
        try:
            db.session.execute(text("ALTER TABLE admins ADD COLUMN reset_token VARCHAR(100)"))
            db.session.commit()
        except Exception:
            db.session.rollback()
        try:
            db.session.execute(text("ALTER TABLE admins ADD COLUMN reset_token_expires DATETIME"))
            db.session.commit()
        except Exception:
            db.session.rollback()


def create_admin_if_not_exists():
    """Cria um admin padrão se não existir"""
    with app.app_context():
        db.create_all()
        migrate_add_quantity()
        migrate_add_discount()
        migrate_add_reset_fields()
        if not Admin.query.first():
            admin = Admin(username='admin', email='admin@telmoz.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin criado: username=admin, password=admin123')


if __name__ == '__main__':
    create_admin_if_not_exists()
    app.run(debug=True, port=5000)

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    """Modelo do administrador"""
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Gera token para reset de senha"""
        import secrets
        from datetime import datetime, timedelta
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token


class Category(db.Model):
    """Modelo de categoria de produtos"""
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    """Modelo de produto"""
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    discount_percent = db.Column(db.Float, default=0.0, nullable=False)  # Desconto em percentagem (0-100)
    quantity = db.Column(db.Integer, default=0, nullable=False)  # Quantidade em stock
    image_url = db.Column(db.String(500))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    whatsapp_message = db.Column(db.String(500))  # Mensagem personalizada para WhatsApp
    
    @property
    def final_price(self):
        """Preço final após desconto"""
        if self.discount_percent > 0:
            return self.price * (1 - self.discount_percent / 100)
        return self.price

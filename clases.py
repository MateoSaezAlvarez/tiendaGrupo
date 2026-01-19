from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/pybbdd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Tabla Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    roles = db.Column(db.String(100), nullable=False)
    
    def __init__(self, username, password, roles):
        self.username = username
        self.password = password
        self.roles = roles
    
    def get_username(self):
        return self.username
    
    def get_password(self):
        return self.password
    
    def get_roles(self):
        return self.roles


class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    
    def __init__(self, nombre, precio, stock):
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
    
    def get_nombre(self):
        return self.nombre
    
    def get_precio(self):
        return self.precio
    
    def get_stock(self):
        return self.stock

class Carrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    
    usuario = db.relationship('Usuario', backref='carritos')
    producto = db.relationship('Producto', backref='carritos')

    def __init__(self, usuario_id, producto_id, cantidad):
        self.usuario_id = usuario_id
        self.producto_id = producto_id
        self.cantidad = cantidad

    def get_usuario_id(self):
        return self.usuario_id
    
    def get_producto_id(self):
        return self.producto_id
    
    def get_cantidad(self):
        return self.cantidad
    
    def get_total(self):
        return self.total

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    carrito_id = db.Column(db.Integer, db.ForeignKey('carrito.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)


class DetallePedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

app = Flask(__name__)
# Ajusta tu conexión si es necesario
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/pybbdd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    roles = db.Column(db.String(100), nullable=False, default='user')
    
    def __init__(self, username, password, roles='user'):
        self.username = username
        self.password = password
        self.roles = roles

class Producto(db.Model):
    __tablename__ = 'producto'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    imagen = db.Column(db.String(200), nullable=True)
    
    def __init__(self, nombre, precio, stock, imagen=None):
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.imagen = imagen

class Carrito(db.Model):
    __tablename__ = 'carrito'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    
    # Relaciones para acceder fácil: item_carrito.producto.nombre
    usuario = db.relationship('Usuario', backref='items_carrito')
    producto = db.relationship('Producto', backref='en_carritos')

    def __init__(self, usuario_id, producto_id, cantidad):
        self.usuario_id = usuario_id
        self.producto_id = producto_id
        self.cantidad = cantidad

class Pedido(db.Model):
    __tablename__ = 'pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    def __init__(self, usuario_id, total):
        self.usuario_id = usuario_id
        self.total = total

    detalles_pedido = db.relationship('DetallePedido', backref='pedido')

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    
    # Relaciones para acceder fácil: detalle_pedido.producto.nombre
    pedido = db.relationship('Pedido', backref='detalles_pedido')
    producto = db.relationship('Producto', backref='detalles_pedido')

    def __init__(self, pedido_id, producto_id, cantidad, precio):
        self.pedido_id = pedido_id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.precio = precio
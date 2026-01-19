import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user

# Importamos modelos y objetos de configuración
from clases import Producto, Usuario, Carrito, Pedido, DetallePedido, app, db, login_manager

# --- CONFIGURACIÓN ---
app.config['UPLOAD_FOLDER'] = 'static/uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- LOGIN ---
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# --- RUTAS PRINCIPALES ---

@app.route('/')
def index():
    query = request.args.get('q')
    if query:
        productos = Producto.query.filter(Producto.nombre.like(f'%{query}%')).all()
    else:
        productos = Producto.query.all()
    return render_template('index.html', productos=productos)  # Cambiado a index.html

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if Usuario.query.filter_by(username=username).first():
            flash("El usuario ya existe.")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password, method='scrypt')
        new_user = Usuario(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Credenciales incorrectas")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- PRODUCTOS (CRUD) ---

@app.route('/producto/<int:id>')
def detalle_producto(id):
    p = Producto.query.get_or_404(id)
    return render_template('producto_detalle.html', producto=p)  # Cambiado a producto_detalle.html

@app.route('/productos/nuevo')
@login_required
def nuevo_producto():
    return render_template('producto_form.html', producto=None)  # Cambiado a producto_form.html

@app.route('/productos/agregar', methods=['POST'])
@login_required
def agregar_producto():
    nombre = request.form['nombre']
    precio = float(request.form['precio'])
    stock = int(request.form['stock'])
    imagen_nombre = 'default.jpg'

    if 'imagen' in request.files:
        file = request.files['imagen']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagen_nombre = filename

    nuevo = Producto(nombre, precio, stock, imagen_nombre)
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/editar/<int:id>')
@login_required
def editar_producto(id):
    p = Producto.query.get_or_404(id)
    return render_template('producto_form.html', producto=p)  # Cambiado a producto_form.html

@app.route('/productos/editar/<int:id>', methods=['POST'])
@login_required
def actualizar_producto(id):
    p = Producto.query.get_or_404(id)
    p.nombre = request.form['nombre']
    p.precio = float(request.form['precio'])
    p.stock = int(request.form['stock'])

    if 'imagen' in request.files:
        file = request.files['imagen']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            p.imagen = filename

    db.session.commit()
    return redirect(url_for('detalle_producto', id=p.id))

@app.route('/eliminar/<int:id>', methods=['GET', 'POST'])
@login_required
def eliminar_producto(id):
    p = Producto.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('index'))

# --- CARRITO PERSISTENTE (BD) ---

@app.route('/carrito/agregar/<int:id>')
@login_required
def agregar_carrito(id):
    item_carrito = Carrito.query.filter_by(usuario_id=current_user.id, producto_id=id).first()

    if item_carrito:
        item_carrito.cantidad += 1
    else:
        nuevo_item = Carrito(usuario_id=current_user.id, producto_id=id, cantidad=1)
        db.session.add(nuevo_item)

    db.session.commit()
    flash("Producto añadido al carrito")
    return redirect(url_for('index'))

@app.route('/carrito')
@login_required
def ver_carrito():
    items_bd = Carrito.query.filter_by(usuario_id=current_user.id).all()
    items = []
    total_global = 0
    for item in items_bd:
        subtotal = item.producto.precio * item.cantidad
        total_global += subtotal
        items.append({
            'producto': item.producto,
            'cantidad': item.cantidad,
            'subtotal': subtotal,
            'id_producto': item.producto.id
        })
    return render_template('carrito.html', items=items, total_global=total_global)

@app.route('/carrito/eliminar/<int:id_prod>')
@login_required
def eliminar_item_carrito(id_prod):
    item = Carrito.query.filter_by(usuario_id=current_user.id, producto_id=id_prod).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Producto eliminado")
    return redirect(url_for('ver_carrito'))

@app.route('/carrito/vaciar')
@login_required
def vaciar_carrito():
    Carrito.query.filter_by(usuario_id=current_user.id).delete()
    db.session.commit()
    flash("Carrito vaciado")
    return redirect(url_for('ver_carrito'))

# --- CHECKOUT ---

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    items_bd = Carrito.query.filter_by(usuario_id=current_user.id).all()
    if not items_bd:
        flash("Tu carrito está vacío.")
        return redirect(url_for('index'))

    total_orden = 0
    for item in items_bd:
        if item.producto.stock < item.cantidad:
            flash(f"Stock insuficiente para {item.producto.nombre}")
            return redirect(url_for('ver_carrito'))
        total_orden += (item.producto.precio * item.cantidad)

    nuevo_pedido = Pedido(usuario_id=current_user.id, total=total_orden)
    db.session.add(nuevo_pedido)
    db.session.commit()

    for item in items_bd:
        detalle = DetallePedido(
            pedido_id=nuevo_pedido.id,
            producto_id=item.producto.id,
            cantidad=item.cantidad,
            precio=item.producto.precio
        )
        item.producto.stock -= item.cantidad
        db.session.add(detalle)
        db.session.delete(item)

    db.session.commit()
    return render_template('index.html', pedido=nuevo_pedido)  # Cambiado a index.html

# --- EJECUTAR APP ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

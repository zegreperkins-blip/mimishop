import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key-before-deployment")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "mimishop.db"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Les photos sont hébergées sur Cloudinary (stockage permanent et partagé).
CLOUDINARY_CONFIGURED = all(os.environ.get(key) for key in (
    "CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"
))
if CLOUDINARY_CONFIGURED:
    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
        secure=True,
    )
db = SQLAlchemy(app)

WHATSAPP = "2250576949824"
STORE_EMAIL = "mariamjoseycamara@gmail.com"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255), default="")
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(255), default="")
    items = db.Column(db.Text, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), default="Nouvelle")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def is_admin():
    return session.get("admin_id") is not None

def cart_details():
    cart = session.get("cart", {})
    products, total = [], 0
    for pid, qty in cart.items():
        product = db.session.get(Product, int(pid))
        if product and qty > 0:
            subtotal = product.price * qty
            products.append({"product": product, "qty": qty, "subtotal": subtotal})
            total += subtotal
    return products, total

@app.context_processor
def global_values():
    return {"store_email": STORE_EMAIL, "whatsapp": "05 76 94 98 24"}

@app.route("/")
def index():
    category = request.args.get("categorie", "")
    search = request.args.get("q", "").strip()
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    products = query.order_by(Product.featured.desc(), Product.created_at.desc()).all()
    return render_template("index.html", products=products, category=category, search=search)

@app.route("/produit/<int:product_id>")
def product_detail(product_id):
    product = db.get_or_404(Product, product_id)
    return render_template("product.html", product=product)

@app.post("/panier/ajouter/<int:product_id>")
def add_to_cart(product_id):
    product = db.get_or_404(Product, product_id)
    if product.stock <= 0:
        flash("Cet article est momentanément indisponible.", "error")
        return redirect(url_for("product_detail", product_id=product.id))
    cart = session.get("cart", {})
    key = str(product.id)
    cart[key] = min(cart.get(key, 0) + 1, product.stock)
    session["cart"] = cart
    flash("Article ajouté au panier.", "success")
    return redirect(request.referrer or url_for("index"))

@app.route("/panier")
def cart():
    products, total = cart_details()
    return render_template("cart.html", items=products, total=total)

@app.post("/panier/modifier")
def update_cart():
    cart = session.get("cart", {})
    for key in list(cart.keys()):
        try:
            qty = max(0, int(request.form.get(key, 0)))
        except ValueError:
            qty = 0
        product = db.session.get(Product, int(key))
        if not product or qty == 0:
            cart.pop(key, None)
        else:
            cart[key] = min(qty, product.stock)
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/commander", methods=["GET", "POST"])
def checkout():
    items, total = cart_details()
    if not items:
        flash("Votre panier est vide.", "error")
        return redirect(url_for("index"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        if not name or not phone:
            flash("Veuillez renseigner votre nom et votre téléphone.", "error")
            return render_template("checkout.html", items=items, total=total)
        lines = []
        for item in items:
            lines.append(f"{item['product'].name} x{item['qty']} = {item['subtotal']:,} FCFA")
        order = Order(customer_name=name, phone=phone, address=address,
                      items=" | ".join(lines), total=total)
        db.session.add(order)
        db.session.commit()
        message = (f"Bonjour MIMISHOP, je souhaite confirmer la commande n°{order.id}. "
                   f"Nom: {name}. Téléphone: {phone}. Adresse: {address or 'À préciser'}. "
                   f"Articles: {'; '.join(lines)}. Total: {total:,} FCFA. Paiement à la livraison.")
        session["cart"] = {}
        from urllib.parse import quote
        return redirect("https://wa.me/" + WHATSAPP + "?text=" + quote(message))
    return render_template("checkout.html", items=items, total=total)

@app.route("/admin/connexion", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin = Admin.query.filter_by(username=request.form.get("username", "")).first()
        if admin and check_password_hash(admin.password_hash, request.form.get("password", "")):
            session["admin_id"] = admin.id
            return redirect(url_for("admin_dashboard"))
        flash("Identifiants incorrects.", "error")
    return render_template("admin_login.html")

@app.route("/admin/deconnexion")
def admin_logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/admin")
def admin_dashboard():
    if not is_admin(): return redirect(url_for("admin_login"))
    return render_template("admin.html", products=Product.query.order_by(Product.created_at.desc()).all(),
                           orders=Order.query.order_by(Order.created_at.desc()).limit(12).all())

@app.route("/admin/produit/nouveau", methods=["GET", "POST"])
@app.route("/admin/produit/<int:product_id>/modifier", methods=["GET", "POST"])
def product_form(product_id=None):
    if not is_admin(): return redirect(url_for("admin_login"))
    product = db.session.get(Product, product_id) if product_id else Product()
    if request.method == "POST":
        product.name = request.form.get("name", "").strip()
        product.category = request.form.get("category", "Robes")
        product.description = request.form.get("description", "").strip()
        product.price = max(0, int(request.form.get("price", 0)))
        product.stock = max(0, int(request.form.get("stock", 0)))
        product.featured = bool(request.form.get("featured"))
        file = request.files.get("image_file")
        upload_error = False
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Format photo non accepté. Utilisez JPG, PNG ou WEBP.", "error")
                upload_error = True
            elif not CLOUDINARY_CONFIGURED:
                flash("Le stockage photo n'est pas encore configuré. Ajoutez les 3 clés Cloudinary dans Render.", "error")
                upload_error = True
            else:
                try:
                    result = cloudinary.uploader.upload(
                        file,
                        folder="mimishop/produits",
                        resource_type="image",
                    )
                    # On enregistre l'URL HTTPS permanente, pas un chemin local Render.
                    product.image = result["secure_url"]
                except Exception:
                    app.logger.exception("Échec de l'envoi de la photo vers Cloudinary")
                    flash("Impossible d'envoyer la photo. Vérifiez les paramètres Cloudinary puis réessayez.", "error")
                    upload_error = True
        elif request.form.get("image_url", "").strip():
            product.image = request.form.get("image_url", "").strip()
        if not product.name:
            flash("Le nom du produit est obligatoire.", "error")
        elif not upload_error:
            db.session.add(product)
            db.session.commit()
            flash("Produit enregistré.", "success")
            return redirect(url_for("admin_dashboard"))
    return render_template("product_form.html", product=product)

@app.post("/admin/produit/<int:product_id>/supprimer")
def delete_product(product_id):
    if not is_admin(): return redirect(url_for("admin_login"))
    product = db.get_or_404(Product, product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Produit supprimé.", "success")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/commande/<int:order_id>/statut")
def update_order(order_id):
    if not is_admin(): return redirect(url_for("admin_login"))
    order = db.get_or_404(Order, order_id)
    order.status = request.form.get("status", "Nouvelle")
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

with app.app_context():
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    db.create_all()
    if not Admin.query.filter_by(username=os.environ.get("ADMIN_USERNAME", "admin")).first():
        db.session.add(Admin(
            username=os.environ.get("ADMIN_USERNAME", "admin"),
            password_hash=generate_password_hash(os.environ.get("ADMIN_PASSWORD", "MimiShop2026!"))
        ))
        db.session.commit()
    if Product.query.count() == 0:
        demo = [
            Product(name="Robe Élégance Orange", category="Robes", description="Robe longue à rayures orange et blanches, manches bouffantes et coupe féminine.", price=15000, stock=8, featured=True),
            Product(name="Abaya Élégance", category="Abayas", description="Abaya élégante pour une allure sobre et raffinée.", price=18000, stock=6, featured=True),
            Product(name="Slip confort", category="Slips", description="Slip féminin confortable. Choisissez votre taille avant confirmation.", price=2500, stock=20),
        ]
        db.session.add_all(demo)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS  

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cars.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)

swagger_ui = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swagger_ui, url_prefix=SWAGGER_URL)

db = SQLAlchemy(app)
ma = Marshmallow(app)

# 🚗 Model Tanımlama
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Temel Bilgiler
    car_name = db.Column(db.String(100), nullable=False)
    car_model = db.Column(db.String(100), nullable=False)
    car_year = db.Column(db.Integer, nullable=False)
    car_image = db.Column(db.String(1000), nullable=False)
    car_category= db.Column(db.String(100), nullable=False)
    
    # Performans Özellikleri
    car_range = db.Column(db.Integer, nullable=False)  # Menzil (km)
    top_speed = db.Column(db.Integer, nullable=False)  # Maksimum hız (km/saat)
    acceleration = db.Column(db.Float, nullable=False)  # 0-100 km/s hızlanma (saniye)
    
    # Batarya ve Şarj Bilgileri
    battery_capacity = db.Column(db.Float, nullable=False)  # Batarya kapasitesi (kWh)
    charge_time = db.Column(db.Float, nullable=False)  # Tam şarj süresi (saat)
    fast_charge_support = db.Column(db.Boolean, default=False)  # Hızlı şarj desteği
    
    # Çekiş ve Sürüş Özellikleri
    drive_type = db.Column(db.String(50), nullable=False)  # Çekiş tipi (Önden Çekiş, Arkadan Çekiş, 4x4)
    autonomous_driving = db.Column(db.Boolean, default=False)  # Otonom sürüş desteği
    seating_capacity = db.Column(db.Integer, nullable=False)  # Koltuk kapasitesi
    
    # Fiyat ve Ekonomi Bilgileri
    price = db.Column(db.Float, nullable=False)  # Araba fiyatı (USD)
    tax_incentive = db.Column(db.Boolean, default=False)  # Vergi indirimi desteği
    
    # Diğer Teknik Detaylar
    weight = db.Column(db.Float, nullable=False)  # Araba ağırlığı (kg)
    length = db.Column(db.Float, nullable=False)  # Araba uzunluğu (metre)
    width = db.Column(db.Float, nullable=False)  # Araba genişliği (metre)
    height = db.Column(db.Float, nullable=False)  # Araba yüksekliği (metre)
    
    # Üretici Bilgileri
    manufacturer = db.Column(db.String(100), nullable=False)  # Üretici firma
    country_of_origin = db.Column(db.String(100), nullable=False)  # Üretim ülkesi
    
# 📦 Schema (JSON formatında dönüşüm için)
class CarSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Car

car_schema = CarSchema()
cars_schema = CarSchema(many=True)

# 🚀 CRUD İşlemleri

# 🔹 Tüm arabaları listele
@app.route("/cars", methods=["GET"])
def get_cars():
    cars = Car.query.all()
    return jsonify(cars_schema.dump(cars))

# 🔹 Tek bir arabayı getir
@app.route("/cars/<int:id>", methods=["GET"])
def get_car(id):
    car = Car.query.get(id)
    return jsonify(car_schema.dump(car)) if car else jsonify({"message": "Car not found"}), 404

# 🔹 Yeni bir araba ekle
@app.route("/cars", methods=["POST"])
def add_car():
    data = request.json
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    new_car = Car(**data)
    db.session.add(new_car)
    db.session.commit()
    return jsonify(car_schema.dump(new_car)), 201

# 🔹 Bir arabayı güncelle
@app.route("/cars/<int:id>", methods=["PUT"])
def update_car(id):
    car = Car.query.get(id)
    if not car:
        return jsonify({"message": "Car not found"}), 404

    data = request.json
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    for key, value in data.items():
        setattr(car, key, value)

    db.session.commit()
    return jsonify(car_schema.dump(car))

# 🔹 Bir arabayı sil
@app.route("/cars/<int:id>", methods=["DELETE"])
def delete_car(id):
    car = Car.query.get(id)
    if not car:
        return jsonify({"message": "Car not found"}), 404

    db.session.delete(car)
    db.session.commit()
    return "", 204

# 📌 Veritabanını oluştur
with app.app_context():
    db.create_all()

# 🚦 Sunucuyu başlat
if __name__ == "__main__":
    app.run(debug=True)
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


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    

    car_name = db.Column(db.String(100), nullable=False)
    car_model = db.Column(db.String(100), nullable=False)
    car_year = db.Column(db.Integer, nullable=False)
    car_image = db.Column(db.String(1000), nullable=False)
    car_category= db.Column(db.String(100), nullable=False)
    

    car_range = db.Column(db.Integer, nullable=False)  
    top_speed = db.Column(db.Integer, nullable=False) 
    acceleration = db.Column(db.Float, nullable=False) 
    
  
    battery_capacity = db.Column(db.Float, nullable=False)
    charge_time = db.Column(db.Float, nullable=False) 
    fast_charge_support = db.Column(db.Boolean, default=False) 
    
    drive_type = db.Column(db.String(50), nullable=False)  
    autonomous_driving = db.Column(db.Boolean, default=False)  
    seating_capacity = db.Column(db.Integer, nullable=False) 
    

    price = db.Column(db.Float, nullable=False) 
    tax_incentive = db.Column(db.Boolean, default=False)  
    

    weight = db.Column(db.Float, nullable=False)  
    length = db.Column(db.Float, nullable=False) 
    width = db.Column(db.Float, nullable=False)  
    height = db.Column(db.Float, nullable=False) 
    

    manufacturer = db.Column(db.String(100), nullable=False) 
    country_of_origin = db.Column(db.String(100), nullable=False) 
    

class CarSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Car

car_schema = CarSchema()
cars_schema = CarSchema(many=True)



@app.route("/cars", methods=["GET"])
def get_cars():
    cars = Car.query.all()
    return jsonify(cars_schema.dump(cars))


@app.route("/cars/<int:id>", methods=["GET"])
def get_car(id):
    car = Car.query.get(id)
    return jsonify(car_schema.dump(car)) if car else jsonify({"message": "Car not found"}), 404


@app.route("/cars", methods=["POST"])
def add_car():
    data = request.json
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    new_car = Car(**data)
    db.session.add(new_car)
    db.session.commit()
    return jsonify(car_schema.dump(new_car)), 201


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


@app.route("/cars/<int:id>", methods=["DELETE"])
def delete_car(id):
    car = Car.query.get(id)
    if not car:
        return jsonify({"message": "Car not found"}), 404

    db.session.delete(car)
    db.session.commit()
    return "", 204


@app.route("/cars/category/<string:category>", methods=["GET"])
def get_cars_by_category(category):
    cars = Car.query.filter(Car.car_category.ilike(category)).all()
    return jsonify(cars_schema.dump(cars))

@app.route("/cars/search", methods=["GET"])
def search_cars():
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify([])

    cars = Car.query.filter(
        db.or_(
            Car.car_name.ilike(f"%{query}%"),
            Car.car_model.ilike(f"%{query}%")
        )
    ).all()
    return jsonify(cars_schema.dump(cars))



with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
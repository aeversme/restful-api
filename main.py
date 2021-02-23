from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import projectsecrets as ps
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route('/random', methods=['GET'])
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all', methods=['GET'])
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route('/search')
def search_for_cafe():
    query_location = request.args.get('loc')
    cafes_near_location = db.session.query(Cafe).filter_by(location=query_location).all()
    if cafes_near_location:
        return jsonify(cafe=[cafe.to_dict() for cafe in cafes_near_location])
    else:
        return jsonify(error={'Not Found': 'Sorry, there are no cafes near that location.'})


# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_a_cafe():
    new_cafe = Cafe(
        name=request.form.get('name'),
        map_url=request.form.get('map_url'),
        img_url=request.form.get('img_url'),
        location=request.form.get('loc'),
        seats=request.form.get('seats'),
        has_toilet=bool(int(request.form.get('toilet'))),
        has_wifi=bool(int(request.form.get('wifi'))),
        has_sockets=bool(int(request.form.get('sockets'))),
        can_take_calls=bool(int(request.form.get('calls'))),
        coffee_price=f"\u00a3{request.form.get('price')}",
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={'success': 'Successfully added the new cafe.'})


# HTTP PUT/PATCH - Update Record
@app.route('/update_price/<int:cafe_id>', methods=['PUT', 'PATCH'])
def update_coffee_price(cafe_id):
    cafe_to_update = Cafe.query.get(cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = f"\u00a3{request.args.get('price')}"
        db.session.commit()
        return jsonify(response={'success': 'Successfully updated the price.'}), 200
    else:
        return jsonify(error={'Not Found': 'Sorry, a cafe with that id was not found in the database.'}), 404


# HTTP DELETE - Delete Record
@app.route('/report_closed/<int:cafe_id>', methods=['DELETE'])
def delete_cafe_record(cafe_id):
    if request.args.get('api_key') == ps.API_KEY:
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={'success': 'Successfully reported a closed cafe.'}), 200
        else:
            return jsonify(error={'Not Found': 'Sorry, a cafe with that id was not found in the database.'}), 404
    else:
        return jsonify(error={'Not Authorized': 'Sorry, that is not allowed. Make sure you have a valid api_key.'}), 403


if __name__ == '__main__':
    app.run(debug=True)

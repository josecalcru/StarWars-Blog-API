"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, People, Vehicles, Favorites


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)



# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#User endpoints ----------------------------
@app.route('/user', methods=['GET'])
def get_users():

    results = User.query.all()
    if not results:
        raise APIException('Cannot find users', status_code=404)
    else:
         # map the results and your list of people  inside of the all_user variable
        all_users = list(map(lambda x: x.serialize(), results))

    return jsonify(all_users), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):

    result = User.query.get(user_id)

    if not result:
        raise APIException('Cannot find user', status_code=404)
    else:
        user = result.serialize()

    return jsonify(user), 200

@app.route('/user', methods=['POST'])
def add_user():
    request_body = request.get_json()
    user = User(fullName=request_body["fullName"],email=request_body["email"],password=request_body["password"],is_active=request_body["is_active"])
    db.session.add(user)
    db.session.commit()
   
    return jsonify({"Result":"successful"}), 200


@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    
    user = User.query.get(user_id)
    if not user:
        raise APIException('Cannot find user', status_code=404)

    request_body = request.get_json()
    if "fullName" in request_body:
        user.fullName = request_body["fullName"]
    if "email" in request_body:
        user.email = request_body["email"]
    if "password" in request_body:
        user.password = request_body["password"]
    if "is_active" in request_body:
        user.is_active = request_body["is_active"]
    db.session.commit()
   
    return jsonify({"Update":"successful"}), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def del_user(user_id):
    
    user = User.query.get(user_id)
    if not user:
        raise APIException('User not found', status_code=404)

    db.session.delete(user)
    db.session.commit()
   
    return jsonify({"Delete":"successful"}), 200
  # End user endpoints ------------------------



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

from flask import Flask, jsonify, request, make_response
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client.bizDB
businesses = db.biz

@app.route('/businesses', methods=['GET'])
def get_all_business():
    data_to_return = []
    try:
        for business in businesses.find():
            business['_id'] = str(business['_id'])
            
            for review in business.get('reviews', []): 
                review['_id'] = str(review['_id'])
            data_to_return.append(business)
        return make_response(jsonify(data_to_return), 200)
    
    except ConnectionError:
        return make_response(jsonify({"error": "Database connection error"}), 500)
    
    except Exception as e:
        return make_response(jsonify({"error": "Internal Server Error", "details": str(e)}), 500)

@app.route('/businesses/<string:id>', methods=['GET'])
def get_one_business(id):
    biz = businesses.find_one({"_id":ObjectId(id)})
    if biz is not None:
        biz["_id"] = str(biz["_id"])
        for review in biz["reviews"]:
            review["_id"] = str(review["_id"])
        return make_response( jsonify(biz), 200 )
    else:
        return make_response(jsonify({"Error" : "Invalid ID"}), 404)

#Business ID 67b501fa1ac72ee4e0bb5234
@app.route('/businesses', methods=['POST'])
def add_business():
    data = request.form
    if data and "name" in data and "town" and "rating" in data:
        new_business = {
            "name": data.get("name"),
            "town": data.get("town"),
            "rating": data.get("rating", 0),
            "reviews": []
        }
        new_business_id = businesses.insert_one(new_business)
        new_business_link = f"http://localhost:5001/businesses/{str(new_business_id)}"
        return make_response(jsonify({"URL": new_business_link}), 200)
    else:
        return make_response(jsonify({"Error":"Missing data"}), 404)

if __name__ == "__main__":
    app.run(debug=True, port = 5001)
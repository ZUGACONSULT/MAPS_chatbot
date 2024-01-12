from flask import Flask, jsonify, render_template, request
from maps import send_loc, is_conform, find_closest_location_type, get_place_reviews

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    locations = send_loc(user_text)
    querry = find_closest_location_type(user_text)
    response = ""
    place_id = ""
    if is_conform(user_text):
      place_id = locations[0]['place_id']
      response += f"Here 5 {querry} around you :<br>"
      for loc in locations:
        response += f"{loc['name']} (Rating: {loc['rating']}) - (Distance: {loc['distance']}) - <a href='{loc['maps_url']}' target='_blank'>View on Map</a><br>"
    else :
      response = send_loc(user_text)
    return jsonify({"message": response, "showReviewButton": is_conform(user_text), "place_id": place_id})


@app.route("/review_summary")
def review_summary():
  place_id = request.args.get('place_id')
  if not place_id:
      return jsonify({"message": "No place ID provided."})

  summary = get_place_reviews(place_id)
  if not summary:
      summary = "No reviews for this location."
    
  return jsonify({"message": summary})


if __name__ == "__main__":
  app.run(host='0.0.0.0',debug=True)  
  
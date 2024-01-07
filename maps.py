import googlemaps
import re
import pandas as pd
from difflib import get_close_matches
import os

my_secret = os.environ['MAPS_PLACES']
# Initialize Google Maps client
gmaps = googlemaps.Client(key=my_secret)

def is_location_query(user_input):
  return re.search(r'\b(where|nearby|near me|location|place|around|closest|nearest)\b', user_input, re.IGNORECASE)

def get_nearby_places(query, location):
  # Fetch places from Google Maps
  places_result = gmaps.places_nearby(location=location, keyword=query, radius=3000)

  # Extract places
  places = places_result['results']

  # Sort places by rating (higher ratings first)
  sorted_places = sorted(places, key=lambda x: x.get('rating', 0), reverse=True)

  # Extract the first 5 places after sorting
  top_places = sorted_places[:5]

  # Extract place names, ratings and Google Maps links
  places_info = []
  for place in top_places:
      name = place['name']
      rating = place.get('rating', 'No rating')
      place_id = place['place_id']
      maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
      places_info.append(f"{name} (Rating: {rating}) - {maps_link}")
      #places_info.append(f'<a href="{maps_link}" target="_blank">{name} (Rating: {rating})</a>')

  return places_info

def get_place_reviews(place_id):
  # Fetch place details
  place_details = gmaps.place(place_id=place_id)

  # Extract reviews
  reviews = place_details.get('result', {}).get('reviews', [])

  # Format reviews (you might want to include more details from each review)
  formatted_reviews = [review['text'] for review in reviews]

  return formatted_reviews

# Load location types from the CSV file
location_types_df = pd.read_csv('places_type.csv', header=None)
location_types = location_types_df.iloc[:, 0].tolist()

def is_location_request(user_input):
  # Basic check to see if the input is a location request
  # This can be improved with more sophisticated NLP techniques
  keywords = ['find', 'search', 'nearby', 'location', 'place', 'near me', 'around']
  return any(keyword in user_input.lower() for keyword in keywords)

def extract_key_terms(text):
  # Remove common words and return a list of key terms
  stop_words = set(['i', 'want', 'to', 'find', 'a', 'nearby', 'please', 'can', 'you', 'me', 'around'])
  words = re.findall(r'\b\w+\b', text.lower())
  key_terms = [word for word in words if word not in stop_words]
  return key_terms

def find_closest_location_type(user_input):
  if is_location_request(user_input):
      # Find the closest match from the location types
      key_terms = extract_key_terms(user_input)
      for term in key_terms:
        closest_match = get_close_matches(term, location_types, n=1, cutoff=0.6)
        if closest_match:
            return closest_match[0]
      return "Could not find a matching location type. Please be more specific."

  else:
      return "Please specify which type of location you are looking for."

def provide_answer(user_input,location="35.77057249176779, -5.808092504868959"):
  if is_location_query(user_input):
    query = find_closest_location_type(user_input)
    if query in location_types:
      places = get_nearby_places(query,location)
      response = "Here are the 5 best " + query +" around you based on reviews:\n" + '\n'.join(places)
      return response
    else : return query
  else:
    return "Your query does not seem to be about locations."
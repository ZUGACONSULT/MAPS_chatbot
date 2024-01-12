import googlemaps
import re
import pandas as pd
from difflib import get_close_matches
import os
import math
from openai import OpenAI

openai_API = os.environ['OPENAI_API']
my_secret = os.environ['MAPS_PLACES']
# Initialize Google Maps client
gmaps = googlemaps.Client(key=my_secret)

# Load location types from the CSV file
location_types_df = pd.read_csv('places_type.csv', header=None)
location_types = location_types_df.iloc[:, 0].tolist()

# Filtering functions

def is_location_query(user_input):
  return re.search(r'\b(where|nearby|near me|location|place|around|closest|nearest)\b', user_input, re.IGNORECASE)

def is_conform(user_input):
  return is_location_query(user_input) and (find_closest_location_type(user_input) in location_types)


# Getting location type

def extract_key_terms(text):
  # Remove common words and return a list of key terms
  stop_words = set(['i', 'want', 'to', 'find', 'a', 'nearby', 'please', 'can', 'you', 'me', 'around'])
  words = re.findall(r'\b\w+\b', text.lower())
  key_terms = [word for word in words if word not in stop_words]
  return key_terms

def find_closest_location_type(user_input):
  if is_location_query(user_input):
      # Find the closest match from the location types
      key_terms = extract_key_terms(user_input)
      for term in key_terms:
        closest_match = get_close_matches(term, location_types, n=1, cutoff=0.6)
        if closest_match:
            return closest_match[0]
      return "Could not find a matching location type. Please be more specific."

  else:
      return "Please specify which type of location you are looking for."


def send_loc(user_input,location="35.77057249176779, -5.808092504868959"):
  if is_location_query(user_input):
    query = find_closest_location_type(user_input)
    if query in location_types:
      places_result = gmaps.places_nearby(location=location, keyword=query, radius=3000)
      # Extract places
      places = places_result['results']
    
      # Sort places by rating (higher ratings first)
      sorted_places = sorted(places, key=lambda x: x.get('rating', 0), reverse=True)
    
      # Extract the first 5 places after sorting
      top_places = sorted_places[:5]
      places_info = []
      for place in top_places :
          name = place['name']
          rating = place.get('rating', 'N/A')
          place_id = place['place_id']
          maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
          place_location = (place['geometry']['location']['lat'], place['geometry']['location']['lng'])
          distance = haversine_distance(location, place_location)
          places_info.append({
              'name': name,
              'rating': rating,
              'maps_url': maps_url,
              'distance': f"{distance:.2f} km",
              'place_id' : place_id
          })
      
      return places_info
    else :
      return query
  else :
    return "Your query does not seem to be about locations."

def haversine_distance(origin, destination):
  coordinates = origin.split(", ")
  origin_tuple = (float(coordinates[0]), float(coordinates[1]))

  lat1, lon1 = origin_tuple
  lat2, lon2 = destination
  radius = 6371  # Earth's radius in kilometers

  dlat = math.radians(lat2 - lat1)
  dlon = math.radians(lon2 - lon1)
  a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
       math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
       math.sin(dlon / 2) * math.sin(dlon / 2))
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  distance = radius * c

  return distance

def get_place_reviews(place_id):
  # Fetch place details
  place_details = gmaps.place(place_id=place_id)

  # Extract reviews
  reviews = place_details.get('result', {}).get('reviews', [])

  # Sort reviews by rating (higher ratings first) and get the top 5
  top_reviews = sorted(reviews, key=lambda x: x.get('rating', 0), reverse=True)[:5]

  # Format reviews into a single text block
  reviews_text = " ".join([review['text'] for review in top_reviews])

  # Call GPT-3.5 to generate a summary
  summary = generate_summary_with_gpt(reviews_text)

  return summary

def generate_summary_with_gpt(reviews_text):
  # Assume you have set your OpenAI API key in your environment variables

  client = OpenAI(api_key=openai_API)
  # Construct a prompt for GPT-3.5 to summarize the reviews
  prompt = f"Summarize the following reviews in 50 words or less:\n\n{reviews_text}"
  
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are a review summarization assistant."},
      {"role": "user", "content": prompt}
    ],
    max_tokens=70,
  )

  # Extract the summary text from the response
  summary = response.choices[0].message.content.strip()

  return summary
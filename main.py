from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from flask import Flask, render_template, url_for, request

# flask declaration and debugging
app = Flask(__name__)


# spotify api token declaration
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# send request to API to get information
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

# construct header when we send a request
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


# # display results for specified category
# def display_results(category, items):
#     print(f"\n{category.capitalize()}:")
#     if not items:
#         print(f"No {category} found.")
#     else:
#         for i, item in enumerate(items, start=1):
#             if category == "artists":
#                 print(f"  {i}. {item['name']}")
#             elif category == "albums":
#                 print(f"  {i}. {item['name']} by {item['artists'][0]['name']}")
#             elif category == "tracks":
#                 print(f"  {i}. {item['name']} by {item['artists'][0]['name']}")

# search function (artists, albums, tracks)
def search_spotify(token, input):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    search_query = f"?q={input}&type=artist,album,track&limit=5"
    result = get(url + search_query, headers=headers)
    return json.loads(result.content)
    
    
# terminal commands 
# token = get_token()
# user_input = input("Search: ")
# result = search_spotify(token, user_input)


    

# main page
@app.route("/", methods=["GET", "POST"])
def index():
    # if user presses enter on the search bar with input
    if request.method == "POST":
        # get the user input
        query = request.form.get("content", "")
        # if there is no user input
        if not query:
            return render_template("index.html", error="Please enter a search term.")
        
        token = get_token()
        results = search_spotify(token, query)

        # list of artists from results
        artists = [
            {
                "name": artist["name"], 
                "image": artist["images"][0]["url"] 
                if artist["images"] else ""
            }
            for artist in results.get("artists", {}).get("items", [])
        ]
        # list of albums from results
        albums = [
            {
                "name": album["name"], 
                "artist": album["artists"][0]["name"], 
                "year": album.get("release_date", "").split("-")[0], 
                "image": album["images"][0]["url"]
            }
            for album in results.get("albums", {}).get("items", [])
        ]
        # list of tracks from results
        tracks = [
            {
                "name": track["name"], 
                "artist": track["artists"][0]["name"], 
                "album": track["album"]["name"], 
                "image": track["album"]["images"][0]["url"]
            }
            for track in results.get("tracks", {}).get("items", [])
        ]
        # return website with the results displayed
        return render_template("index.html", artists=artists, albums=albums, tracks=tracks)
    # default landing page
    else:
        return render_template("index.html")
if __name__ == "__main__":
    app.run(debug=True)
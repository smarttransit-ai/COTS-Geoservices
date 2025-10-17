import requests
from dotenv import load_dotenv
import os
import json
load_dotenv()

# Read environment variables
OSRM_HOST = os.getenv("OSRM_HOST", "localhost")
OSRM_PORT = os.getenv("OSRM_PORT", 8080)
OSRM_URL = f"{OSRM_HOST}:{OSRM_PORT}/nearest/v1/driving/"

OTP_HOST = os.getenv("OTP_HOST", "localhost")
OTP_PORT = os.getenv("OTP_PORT", 8083)
OTP_URL = f"http://{OTP_HOST}:{OTP_PORT}"

VROOM_HOST = os.getenv("VROOM_HOST", "localhost")
VROOM_PORT = os.getenv("VROOM_PORT", 3000)
VROOM_URL = f"http://{VROOM_HOST}:{VROOM_PORT}"

VALHALLA_HOST = os.getenv("VALHALLA_HOST", "localhost")
VALHALLA_PORT = os.getenv("VALHALLA_PORT", 8002)
VALHALLA_URL = f"http://{VALHALLA_HOST}:{VALHALLA_PORT}/status"

NOMINATIM_HOST = os.getenv("NOMINATIM_HOST", "localhost")
NOMINATIM_PORT = os.getenv("NOMINATIM_PORT", 8081)
NOMINATIM_URL = f"http://{NOMINATIM_HOST}:{NOMINATIM_PORT}"

PHOTON_HOST = os.getenv("PHOTON_HOST", "localhost")
PHOTON_PORT = os.getenv("PHOTON_PORT", 2322)
PHOTON_URL = f"http://{PHOTON_HOST}:{PHOTON_PORT}"

OVERPASS_HOST = os.getenv("OVERPASS_HOST", "localhost")
OVERPASS_PORT = os.getenv("OVERPASS_PORT", 1234)
OVERPASS_URL = f"http://{OVERPASS_HOST}:{OVERPASS_PORT}/api"

def check_overpass():
    response = requests.post(OVERPASS_URL + '/interpreter', headers = {"Connection": "close", "Content-Type": "text/plain; charset=UTF-8"}, data='''
    [out:json][timeout:180];
    (
    node["amenity"="cafe"](36.05,-87.0,36.34,-86.6);
    way["amenity"="cafe"](36.05,-87.0,36.3,-86.6);
    relation["amenity"="cafe"](36.05,-87.0,36.3,-86.6);
    );
    out center;
    ''')
    if response.status_code == 200:
        data = response.json()
        if 'elements' in data:
            print(f"Success: {OVERPASS_URL} is reachable.")
            return
    print(f"Error: {OVERPASS_URL} failed with status code {response.status_code}.")

if __name__ == "__main__":
    print("Verifying deployment...")
    print(f"OSRM URL: {OSRM_URL}")
    print(f"OTP URL: {OTP_URL}")
    print(f"VROOM URL: {VROOM_URL}")
    print(f"VALHALLA URL: {VALHALLA_URL}")
    print(f"NOMINATIM URL: {NOMINATIM_URL}")
    print(f"PHOTON URL: {PHOTON_URL}")
    print(f"OVERPASS URL: {OVERPASS_URL}")

    # Create a function that would query a url and see if it is 200.
    def check_url(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Success: {url} is reachable.")
            else:
                print(f"Error: {url} returned status code {response.status_code}.")
        except Exception as e:
            print(f"Exception: {e}")

    # Check all URLs
    check_url(f"http://{OSRM_URL}-86.9024502,35.9067283")
    check_url(OTP_URL)
    check_url(f"{VROOM_URL}/health")
    check_url(VALHALLA_URL)
    check_url(f"{NOMINATIM_URL}/search?q=Memphis&format=json")
    check_url(f"{PHOTON_URL}/api?q=Nashv&limit=1")
    check_overpass()

import requests

OSRM_HOST = "localhost"
OSRM_PORT = 8080
OSRM_URL = f"{OSRM_HOST}:{OSRM_PORT}/nearest/v1/driving/"
OTP_HOST = "localhost"
OTP_PORT = 8081
OTP_URL = f"http://{OTP_HOST}:{OTP_PORT}"
VROOM_HOST = "localhost"
VROOM_PORT = 3000
VROOM_URL = f"http://{VROOM_HOST}:{VROOM_PORT}"
VALHALLA_HOST = "localhost"
VALHALLA_PORT = 8002
VALHALLA_URL = f"http://{VALHALLA_HOST}:{VALHALLA_PORT}/status"

if __name__ == "__main__":
    print("Verifying deployment...")
    print(f"OSRM URL: {OSRM_URL}")
    print(f"OTP URL: {OTP_URL}")
    print(f"VROOM URL: {VROOM_URL}")

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

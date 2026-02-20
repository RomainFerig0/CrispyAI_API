"""
Runs docker-compose up
Fetches random ngrok URL
"""

import os
from dotenv import load_dotenv
import requests
import urllib3.exceptions

load_dotenv() # Loading environmental variables

if os.getenv("MODE") not in ["local", "container"]:
    raise ValueError("Illegal execution parameter")

api_mode = os.getenv("MODE")

if api_mode == "container":

    try:
        r = requests.get("http://localhost:4040/api/tunnels")

        if r.status_code == 200: 
            message = "ngrok URL at: \n"
            res = r.json()

            for i in res['tunnels']:
                message = message + i['public_url'] +'\n'

            print (message)
        else :
            raise ConnectionError("Error:", r.status_code, ", cannot reach Ngrok.")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except urllib3.exceptions.NewConnectionError as e:
        print(f"The server isn't running on this machine: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

else:
    print("Ngrok isn't running.")

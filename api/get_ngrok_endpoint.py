"""
Runs docker-compose up
Fetches random ngrok URL
"""

import os
from dotenv import load_dotenv
import time
import requests

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
            print("Cannot reach Ngrok:", r.status_code)


    except Exception as e:
        print("Error: ", e.args) 

else:
    print("Ngrok isn't running.")

import os
import requests
import time

from dotenv import load_dotenv

load_dotenv()

# MySQL Connection Info from .env
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

username = "oliveranderson"
password = "P@ssw0rd123"

# Register User
def registerUser():
    try:
        register_response = requests.post("http://localhost:8000/auth/register", json={"username": username, "password": password})
        if register_response.status_code == 400:
            print(register_response.json()["detail"])
        else:
            print(register_response.json())
    except Exception as e:
        print (e)
        pass

# Login User
def loginUser():
    try:
        global access_token, refresh_token
        login_response = requests.post("http://localhost:8000/auth/login", data={"username": username, "password": password})
        
        if login_response.status_code == 401:
            print(login_response.json()["detail"])
        else:
            print(login_response.json())
            access_token = login_response.json()["access_token"]
            refresh_token = login_response.json()["refresh_token"]
    except Exception as e:
        print(e)
        pass

# User information
def showMe():
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        show_response = requests.get("http://localhost:8000/auth/me", headers = headers)
        if show_response.status_code == 401:
            print(show_response.json()['detail'])
        else:
            print(show_response.json())
    except Exception as e:
        print(e)
        pass

def refreshToken():
    try:
        global access_token, refresh_token
        headers = {"Authorization": f"Bearer {refresh_token}"}
        refresh_response = requests.post("http://localhost:8000/auth/refresh", headers = headers)
        if refresh_response.status_code == 401:
            print(refresh_response.json()['detail'])
        else:
            print(refresh_response.json())
            access_token = refresh_response.json()["access_token"]
            refresh_token = refresh_response.json()["refresh_token"]
    except Exception as e:
        print(e)
        pass

if __name__ == "__main__":
    print("####### Register Testing #######")
    registerUser()
    print("####### Login Testing #######")
    loginUser()
    print("####### Get User Testing #######")
    showMe()
    print("####### Pending 10 seconds #######")
    time.sleep(10)
    print("####### Get User Testing Again #######")
    showMe()
    print("####### Refresh Token Testing #######")
    refreshToken()
    print("####### Pending 3 seconds #######")
    time.sleep(3)
    print("####### Get User Testing Again #######")
    showMe()
from kiteconnect import KiteConnect
import os

API_KEY = os.environ.get("KITE_API_KEY")
API_SECRET = os.environ.get("KITE_API_SECRET")
REQUEST_TOKEN = os.environ.get("KITE_REQUEST_TOKEN")

kite = KiteConnect(api_key=API_KEY)
data = kite.generate_session(REQUEST_TOKEN, api_secret=API_SECRET)
print("ACCESS_TOKEN:", data.get("access_token"))
print("USER_ID:", data.get("user_id"))

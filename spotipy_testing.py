from dotenv import load_dotenv
import os
#getting things that shouldn't be committed
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

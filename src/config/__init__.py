import pymongo
import os
import certifi

import hashlib
import pymongo
import certifi
import os
from datetime import datetime
# from dotenv import load_dotenv

# load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")


ca = certifi.where()
mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)


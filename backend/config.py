import os

class Config:
    MONGO_URI = os.getenv('MONGO_URI') or 'mongodb://localhost:27017/the_veiled_realm'

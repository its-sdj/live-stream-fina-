from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['my_database']
users = db['users']

def create_user(username, password):
    user = {
        'username': username,
        'password': password
    }
    users.insert_one(user)

def find_user(username):
    return users.find_one({'username': username})
from pymongo import MongoClient
from bson import json_util
import json
from argon2 import PasswordHasher
import os
from difflib import SequenceMatcher

# connect to mongoDB
mongo = MongoClient("mongodb+srv://vercel-admin-user:OG63gOiWzBd6CSHr@cluster0.nzeny4x.mongodb.net/?retryWrites=true&w=majority")
# get users collection
usersCollection = mongo.test.users
hasher = PasswordHasher()
yes = ["yes", "y", "Yes", "Y"]

# convert BSON to JSON
def parse_json(data):
    return json.loads(json_util.dumps(data))

# find the ratio of the users name and password
def similar(name, password):
    return SequenceMatcher(name, password).ratio() > 0.8

# rates the password based on a number of factors
def rate_password(password):
    points = 0
    if len(password) >= 8:
        points += 1
    if any(char.isdigit() for char in password):
        points += 1
    if any(char.isupper() for char in password):
        points += 1
    if any(char.islower() for char in password):
        points += 1
    if any(not char.isalnum() for char in password):
        points += 1
    if len(password) >= 15:
        points += 1
    return points

# register a user
def register(name, email, password):
    user = usersCollection.find_one({ "email": email })
    if user:
        return "User with that email already exists"
    hashed_password = hasher.hash(password)
    user = { "name": name, "email": email, "password": hashed_password }
    usersCollection.insert_one(user)
    return "User created successfully"

# change a users password
def change_password(email, password):
    user = usersCollection.find_one({ "email": email })
    if not user:
        return "User does not exist"
    hashed_password = hasher.hash(password)
    usersCollection.update_one({ "_id": user["_id"] }, { "$set": { "password": hashed_password } })
    return "Password changed successfully"

# propmt selection
print("1) Create a new user")
print("2) Change a password")
print("3) Display all users")
print("4) Quit")
selection = input("Enter Selection: ")

# validate selection
while not selection.isdigit() or int(selection) not in range(1, 6):
    print("Invalid selection")
    selection = input("Enter Selection: ")

# create new user if user selects 1
if int(selection) == 1:
    name = input("Enter name: ")
    email = input("Enter email: ")
    if usersCollection.find_one({ "email": email }):
        print("User with that email already exists")
        exit()
    password = input("Enter password: ")
    while rate_password(password) <= 2:
        print("Password is too weak")
        password = input("Enter new password: ")
    if rate_password(password) == 2 or rate_password(password) == 3:
        print("This password could be improved.")
        change = input("Would you like to change it? (y/n): ")
        if change in yes:
            password = input("Enter new password: ")
            while rate_password(password) <= 2:
                print("Password is too weak")
                password = input("Enter new password: ")
    if rate_password(password) >= 5:
        print("This is a strong password.")
    print(register(name, email, password))
# change password if user selects 2
elif int(selection) == 2:
    email = input("Enter email: ")
    if not usersCollection.find_one({ "email": email }):
        print("No user with that email exists")
        exit()
    password = input("Enter new password: ")
    while rate_password(password) <= 2:
        print("Password is too weak")
        password = input("Enter new password: ")
    if rate_password(password) == 2 or rate_password(password) == 3:
        print("This password could be improved.")
        change = input("Would you like to change it? (y/n): ")
        if change in yes:
            password = input("Enter new password: ")
            while rate_password(password) <= 2:
                print("Password is too weak")
                password = input("Enter new password: ")
    if rate_password(password) >= 5:
        print("This is a strong password.")
    print(change_password(email, password))
# print all users if they select 3
elif int(selection) == 3:
    for user in usersCollection.find():
        print(parse_json(user))
# end program if user selects 4
elif int(selection) == 4:
    exit()

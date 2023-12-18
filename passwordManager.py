from cryptography.fernet import Fernet
import json
import hashlib
import getpass
import os
import sys
import pyperclip

def main():
    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Do you want to add passwords for websites? ")
        print("4.Exit")

        choice = input("\nWhat are you going to do?(select the choice): ")

        if choice == "1":
            file = 'user_data.json'
            if os.path.exists(file) and os.path.getsize(file) == False:
                print("\n[-] Already exists the master!")
                sys.exit()
            else:
                username = input("Enter your username: ")
                master_password = getpass.getpass("Enter your master password: ")
                register(username, master_password)

        elif choice == "2":
            file = 'user_data.json'
            if os.path.exists(file):
                username = input("Enter your username: ")
                master_password = getpass.getpass("Enter your master password: ")
                login(username, master_password)
            else:
                print("\n[-] You have not registered. Please register!")
                sys.exit()

        elif choice == "3":
            while True:
                print("\n1. Add password")
                print("2. Get password")
                print("3. View saved websites")
                print("4. Exit")

                password_choice = input("Enter your choice: ")

                if password_choice == "1":
                    website = input("Enter the website name: ")
                    password = getpass.getpass("Enter password for the website: ")
                    add_password(website, password)
                    print("[+] Password saved!")

                elif password_choice == "2":
                    website = input("Enter website name: ")
                    decrypted_password = get_password(website)
                    if website and decrypted_password:
                        pyperclip.copy(decrypted_password)
                        print(f"{website}:{decrypted_password} saved to the clipboard!")
                    else:
                        print("Password not found!")

                elif password_choice == "3":
                    view_websites()

                elif password_choice == "4":
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")
        else:
            break

# Hashing the master password
def hashed_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode())
    return sha256.hexdigest()

# Generate a key
def generate_key():
    return Fernet.generate_key()

# Initialize the key
def initialize_key(key):
    return Fernet(key)

# Encrypting the password
def encrypt_password(cipher, password):
    return cipher.encrypt(password.encode()).decode()

# Decrypting function
def decrypt_password(cipher, encrypted_password):
    return cipher.decrypt(encrypted_password.encode()).decode()

# Registering the password for the user
def register(username, master_password):
    # Encrypting the password before storing it
    hash_master_password = hashed_password(master_password)
    user_data = {"username": username, "master_password": hash_master_password}
    file_name = "user_data.json"
    if os.path.exists(file_name):
        print("User already registered.")
    else:
        with open(file_name, "w") as file:
            json.dump(user_data, file)
            print("Registration successful!")

# Login for the user
def login(username, entered_password):
    try:
        with open("user_data.json", "r") as file:
            user_data = json.load(file)
        stored_hashed_password = user_data.get("master_password")
        entered_hashed_password = hashed_password(entered_password)
        if entered_hashed_password == stored_hashed_password and username == user_data.get("username"):
            print("Login successful!")
        else:
            print("User name or password incorrect. Please try again!")
            sys.exit()
    except FileNotFoundError:
        print("You have not registered!")
        sys.exit()

# Function to view saved websites
def view_websites():
    try:
        with open('password.json', 'r') as data:
            view = json.load(data)
            print("\nWebsites you saved...\n")
            for x in view:
                print(x['website'])
            print('\n')
    except FileNotFoundError:
        print("\nYou have not saved any passwords!\n")

# Load or generate the encryption key
key_filename = 'encryption_key.key'
if os.path.exists(key_filename):
    with open(key_filename, 'rb') as key_file:
        key = key_file.read()
else:
    key = generate_key()
    with open(key_filename, 'wb') as key_file:
        key_file.write(key)

cipher = initialize_key(key)

def add_password(website, password):
    if not os.path.exists('password.json'):
        data = []
    else:
        try:
            with open('password.json', 'r') as file:
                data = json.load(file)

        except json.JSONDecodeError:
            data = []

    encrypted_password = encrypt_password(cipher, password)
    password_entry = {'website': website, 'password': encrypted_password}
    data.append(password_entry)

    with open('password.json', 'w') as file:
        json.dump(data, file, indent=4)

def get_password(website):
    if not os.path.exists('password.json'):
        return None
    try:
        with open('password.json', 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        data = []

    for entry in data:
        if entry['website'] == website:
            decrypted_password = decrypt_password(cipher, entry['password'])
            return decrypted_password
    return None

if __name__ == "__main__":
    main()

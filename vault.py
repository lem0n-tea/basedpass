import sqlite3
import os

import cryptography

from data_encryption import *
from password_generator import generate_random_string


class Vault:
    def __init__(self, name, password):
        self.vault_name = name
        self.connection = None
        self.cursor = None
        self.master_password = password
        self.key = None
        self.validation_row_id = 1

    def create_vault(self):
        # Creating path to the new vault
        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory, 'vaults')

        # Create directory if it does not exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        vault_path = os.path.join(folder_path, f'{self.vault_name}.db')

        # Connect to the new database
        self.connection = sqlite3.connect(vault_path)
        self.cursor = self.connection.cursor()
        # Create table 'vault' to store all data
        create_table_query = '''CREATE TABLE vault (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    username TEXT,
                    password TEXT NOT NULL,
                    link TEXT
                    )'''

        self.cursor.execute(create_table_query)

        # Create a table to validate password when db is accessed in the future
        # Stores randomly generated string and its encrypted version
        create_validation_table_query = '''CREATE TABLE validation (
                    id INTEGER PRIMARY KEY,
                    plain_text TEXT,
                    encrypted_text TEXT
                    )'''

        self.cursor.execute(create_validation_table_query)

        # Generate a key for Fernet encryption based on master password
        self.key = generate_key(self.master_password, self.vault_name)

        # Populate validation table
        plain_text = generate_random_string(32)
        encrypted_text = encrypt(plain_text, self.key)

        insert_validation_query = "INSERT INTO validation (id, plain_text, encrypted_text) VALUES (?, ?, ?)"
        self.cursor.execute(insert_validation_query, (self.validation_row_id, plain_text, encrypted_text))

        self.connection.commit()

    def open_vault(self):
        # Form path to the vault
        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory, 'vaults')
        vault_path = os.path.join(folder_path, f'{self.vault_name}.db')

        self.connection = sqlite3.connect(vault_path)
        self.cursor = self.connection.cursor()

        # Extract data for master password validation
        self.cursor.execute('SELECT plain_text, encrypted_text FROM validation WHERE id = ?', (self.validation_row_id,))
        validation_samples = [sample for sample in self.cursor.fetchall()[0]]

        self.key = generate_key(self.master_password, self.vault_name)

        # If decrypted string matches its plain version return True, else return False
        encrypted_text_idx = 1
        try:
            validation_samples[encrypted_text_idx] = decrypt(validation_samples[encrypted_text_idx], self.key)
            return True
        except cryptography.fernet.InvalidToken:
            # Exception is thrown when data cannot be decrypted with a provided key
            return False

    def add_new_profile(self, profile_name, password, username=None, link=None):
        if self.get_profile_id(profile_name) is not None:
            # Profile already exists
            return None

        insert_query = "INSERT INTO vault (name, username, password, link) VALUES (?, ?, ?, ?)"
        # Encrypt all fields to provide them to insertion query
        profile_data = encrypt_many([profile_name, username, password, link], self.key)

        try:
            self.cursor.execute(insert_query, tuple(profile_data))
            self.connection.commit()
        except sqlite3.IntegrityError:
            # Table constraints failed
            # Fields contain invalid data. profile_name and password cannot be None
            return None

    def update_profile(self, profile_name, username, password, link):
        # Find id that relates to profile_name
        search_id = self.get_profile_id(profile_name)
        if search_id is None:
            return None

        # Encrypt new data and append found id to profile_data
        profile_data = encrypt_many([username, password, link], self.key)
        profile_data.append(search_id)
        self.cursor.execute('UPDATE vault SET username = ?, password = ?, link = ? WHERE id = ?',
                            tuple(profile_data))
        self.connection.commit()

    def delete_profile(self, profile_name):
        # Find id that relates to profile_name
        search_id = self.get_profile_id(profile_name)
        if search_id is None:
            return None

        delete_query = f"DELETE FROM vault WHERE id='{search_id}'"
        self.cursor.execute(delete_query)
        self.connection.commit()

    def get_vault_content(self):
        # Extract all profiles from the vault
        self.cursor.execute("SELECT name, username, password, link FROM vault")
        vault_content = self.cursor.fetchall()

        # Decrypt each profile
        for i in range(len(vault_content)):
            profile = list(vault_content[i])
            profile = decrypt_many(profile, self.key)
            vault_content[i] = profile

        return vault_content

    def get_profile(self, profile_name):
        # Find id that relates to profile_name
        search_id = self.get_profile_id(profile_name)
        if search_id is None:
            return None

        self.cursor.execute('SELECT name, username, password, link FROM vault WHERE id = ?', (search_id,))
        # self.cursor.fetchall()[0] returns a tuple with all extracted data
        profile = list(self.cursor.fetchall()[0])

        profile = decrypt_many(profile, self.key)

        return profile

    def close_vault(self):
        self.connection.close()

    def extract_all_profile_names(self):
        # Extract all profile names with correlating ids
        self.cursor.execute('SELECT id, name FROM vault')
        all_profile_names = dict(self.cursor.fetchall())

        # Decrypt all profile names
        for id in all_profile_names:
            all_profile_names[id] = decrypt(all_profile_names[id], self.key)

        return all_profile_names

    def get_profile_id(self, profile_name):
        # Find id that relates to profile_name
        profiles = self.extract_all_profile_names()
        for found_id, name in profiles.items():
            if name == profile_name:
                return found_id

        return None

import sqlite3

from password_generator import generate_pass
from secrets import choice
import pyperclip
from tabulate import tabulate
from vault import Vault

MAIN_MENU = '''\nMenu options:
    [C] - Create a new vault
    [O] - Open an existing vault
    [Q] - Quit'''
VAULT_MENU = '''\nVault options:
    [A] - Add a new profile
    [F] - Find a profile
    [S] - Show all data
    [E] - Exit'''
PROFILE_MENU = '''\nProfile options:
    [U] - Update profile
    [D] - Delete profile
    [E] - Exit'''
PASSWORD_MENU = '''Options:
    [R] - Generate random password
    [M] - Manual input'''
FIELDS = ['Name', 'Username', 'Password', 'Link']

PROFILE_NAME_IDX = 0
USERNAME_IDX = 1
PASSWORD_IDX = 2
LINK_IDX = 3


# Check if new profile name is unique for vault
def is_in_db(vault, new_name):
    names = vault.extract_all_profile_names()

    if new_name in names.values():
        return True

    return False


# Set a password
def set_password():
    print(PASSWORD_MENU)

    while True:
        option = input("Choose the option: ").upper()
        # Manual input
        if option == 'M':
            while True:
                password = input("Enter the password: ")
                if password != '':
                    break
                else:
                    print("Password can not be empty")
            break
        # Generate random password
        elif option == 'R':
            password = generate_pass(length=choice(range(18, 24)))
            break
        else:
            print("Wrong input. Try again")

    # Copy password to the clipboard
    pyperclip.copy(password)
    print("The password has been copied to the clipboard")
    return password


# Add a new profile to the vault
def make_new_profile(vault):
    print("Adding new profile...")

    # Set a new profile name and perform its validation
    while True:
        profile_name = input("Enter a profile name: ")
        if profile_name == '':
            print("Profile name can not be empty")
            continue
        elif is_in_db(vault, profile_name):
            print(f'Profile name should be unique. "{profile_name}" already exists')
            continue
        else:
            break

    # Set username (can be empty)
    username = input("Enter a username (to skip - press Enter): ")
    if username == '':
        username = None

    # Set password
    print("Enter a password")
    password = set_password()

    # Set link (can be empty)
    link = input("Enter a link to the service (to skip - press Enter): ")
    if link == '':
        link = None

    if (profile_name is None or profile_name == '') or (password is None or password == ''):
        print("Fields 'username' or 'password' cannot store entered data. Try to create another profile")
    else:
        vault.add_new_profile(profile_name=profile_name, username=username, password=password, link=link)
        print("The new profile has been successfully added")


# Find a profile in the vault
def find_profile(vault):
    profile_name = input("Enter a profile name: ")

    # Check if profile_name exists in the vault
    if not is_in_db(vault, profile_name):
        print("Profile does not exist in this vault")
        return

    found_profile = vault.get_profile(profile_name)

    profile_name = found_profile[PROFILE_NAME_IDX]
    password = found_profile[PASSWORD_IDX]

    if (profile_name is None or profile_name == '') or (password is None or password == ''):
        print("Error occurred whilst trying to extract the profile data.")
    else:
        print(f'Profile "{profile_name}" has been found')

        # Copy password to the clipboard
        pyperclip.copy(password)
        print("The password has been copied to the clipboard")

        # Enter the profile menu
        profile_menu(vault, profile_name)


# Display data from the vault
def display_content(data):
    print(tabulate(data, headers=FIELDS, tablefmt='fancy_grid'))


# Change existing profile in the vault
def change_profile(vault, profile_name, profile_data):
    print("Updating a profile...")

    # Username update (If Enter is pressed leave the same value)
    username = input("Enter a new username (to skip - press Enter): ")
    if username == '':
        username = profile_data[USERNAME_IDX]

    # Password update
    password = input("Entering a new password [Enter] - to skip, [Any key] - to continue: ")
    if password == '':
        password = profile_data[PASSWORD_IDX]
    else:
        password = set_password()

    # Link update
    link = input("Enter a new link to the service (to skip - press Enter): ")
    if link == '':
        link = profile_data[LINK_IDX]

    vault.update_profile(profile_name, username=username, password=password, link=link)
    print(f'The profile "{profile_name}" has been successfully updated')


# Remove the profile from the vault
def remove_profile(vault, profile_name):
    vault.delete_profile(profile_name)


def profile_menu(vault, profile_name):
    while True:
        # Always extract and display relevant profile data
        profile_data = vault.get_profile(profile_name)
        display_content([profile_data])

        print(PROFILE_MENU)
        option = input("Choose an option: ").upper()

        match option:
            # Update the profile
            case 'U':
                print()
                change_profile(vault, profile_name, profile_data)

            # Delete the profile
            case 'D':
                vault.delete_profile(profile_name)
                print(f'\nProfile "{profile_name}" has been deleted')
                break

            # Exit to the vault menu
            case 'E':
                print("\nExiting the profile...")
                break

            # Wrong user input
            case _:
                print("\nWrong input. Try again")


# Vault menu
def vault_menu(vault):
    while True:
        print(VAULT_MENU)
        option = input("Choose an option: ").upper()

        match option:
            # Exit the vault to the main menu
            case 'E':
                vault.close_vault()
                print("\nExiting the vault...")
                break

            # Add a new profile to the opened vault
            case 'A':
                print()
                make_new_profile(vault)

            # Find a profile in the opened vault
            case 'F':
                print()
                find_profile(vault)

            # Show all data in the opened vault
            case 'S':
                print()
                display_content(vault.get_vault_content())

            # Wrong user input
            case _:
                print("\nWrong input. Try again")


# Main (starting) menu
def main_menu():
    while True:
        print(MAIN_MENU)
        option = input("Choose an option: ").upper()

        match option:
            # Create a new vault (database)
            case 'C':
                vault_name = input("Enter the new vault name: ")
                master_password = input(f'Enter master password for {vault_name}: ')
                vault = Vault(vault_name, master_password)
                try:
                    vault.create_vault()

                    print(f'The vault "{vault_name}" has been successfully created')
                    vault_menu(vault)
                except sqlite3.OperationalError:
                    print(f'Vault "{vault_name}" already exists')

            # Open an existing vault
            case 'O':
                vault_name = input("Enter the vault name: ")
                master_password = input("Enter master password: ")
                vault = Vault(vault_name, master_password)

                try:
                    if vault.open_vault():
                        print(f'The vault "{vault_name}" has been successfully opened')
                        vault_menu(vault)
                    else:
                        print(f'Wrong master password! Failed to access "{vault_name}"')
                        vault.close_vault()
                except sqlite3.OperationalError:
                    print(f'Vault "{vault_name}" does not exist. Try creating it first')

            # Quit the app
            case 'Q':
                print("Finishing up... See you soon!")
                break

            # Wrong user input
            case _:
                print("Wrong input. Try again")

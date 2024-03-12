import secrets
import string

letters = string.ascii_letters
digits = string.digits
special_chars = string.punctuation


def if_intersect(str1, str2):
    # returns True if at least one character from str2 is in str1
    return any(character in str1 for character in str2)


def generate_pass(length, characters=(letters, digits, special_chars,)):
    # Create pool of characters
    alphabet = ''
    for element in characters:
        alphabet += element

    password = ""
    while True:
        for i in range(length):
            password += "".join(secrets.choice(alphabet))

        # Ensures all instances of character sets from alphabet are present in password
        for element in characters:
            if not if_intersect(element, password):
                password = ""
                continue
        break

    return password


def generate_random_string(length):
    alphabet = letters + digits + special_chars
    result = ""

    for i in range(length):
        result += "".join(secrets.choice(alphabet))

    return result

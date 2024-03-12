import unittest

import password_generator
from vault import Vault
from password_generator import *


class TestVault(unittest.TestCase):
    def setUp(self):
        self.vault = Vault('test', '123')
        self.vault.open_vault()

        self.empty_vault = Vault('emptyvault', 'qwerty')
        self.empty_vault.open_vault()

    def test_empty_vault_read(self):
        self.assertEqual(self.empty_vault.get_vault_content(), [])
        self.assertEqual(self.empty_vault.get_profile('steam'), None)

    def test_invalid_data_input(self):
        try:
            self.vault.add_new_profile(profile_name=None, password=None, username=None, link=None)
            self.vault.add_new_profile(profile_name='github', password=None, username=None, link=None)
            self.vault.add_new_profile(profile_name=None, password='1234', username=None, link=None)
        except Exception as e:
            self.fail(f"Raised {type(e)} unexpectedly!")

    def test_not_unique_profile_name(self):
        self.assertEqual(self.vault.add_new_profile('gmail', '123'), None)

    def test_get_profile(self):
        profiles_data = {
            'gmail': ['gmail', 'username@gmail.com', r'6"T[~$v!vJf`<g/ea;0)bz', 'gmail.com'],
            'vk': ['vk', 'newbox@yandex.ru', 'qwerty123', 'vk.com'],
            'steam': ['steam', 'playerone', r'7JcS%<r<!Nn-]&c([87zT', None],
            'ozon': ['ozon', None, 'securepassword', None],
            'Яндекс': ['Яндекс', 'sam.sepi0l@yandex.ru', r'cT/YAMT1HY3+iyYRmF$t0E', None]
        }
        for name in profiles_data.keys():
            self.assertEqual(self.vault.get_profile(name), profiles_data[name])

    def test_open_vault(self):
        self.vault1 = Vault('test', 'qwerty')
        self.vault2 = Vault('test', '123')
        self.vault3 = Vault('test', '')

        self.assertEqual(self.vault1.open_vault(), False)
        self.assertEqual(self.vault2.open_vault(), True)
        self.assertEqual(self.vault3.open_vault(), False)

    def tearDown(self):
        self.vault.close_vault()


class TestPasswordGenerator(unittest.TestCase):
    def setUp(self):
        self.lengths = [13, 24, 89, 0]

    def test_generate_random_string(self):
        for length in self.lengths:
            self.assertEqual(len(generate_random_string(length)), length)

    def test_generate_pass(self):
        self.assertTrue(if_intersect(letters+special_chars, generate_pass(13, (special_chars, letters))))
        self.assertTrue(if_intersect(digits, generate_pass(9, (digits,))))
        self.assertFalse(if_intersect(special_chars, generate_pass(64, (digits, letters))))


if __name__ == '__main__':
    unittest.main()

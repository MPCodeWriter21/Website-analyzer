import unittest
from main import Handler, is_valid_url

obj = Handler()


class TestHandlerFunctions(unittest.TestCase):

    def test_url_checker(self):
        self.assertTrue(is_valid_url("https://www.google.com"))
        self.assertFalse(is_valid_url("https;//www.google.com"))
        self.assertTrue(is_valid_url("google.com"))
        self.assertTrue(is_valid_url("www.google.com"))

    def test_url_protocol(self):
        self.assertEqual("https", check_protocol("https://www.google.com"))
        self.assertEqual("http", check_protocol("http://www.google.com"))


if __name__ == '__main__':
    unittest.main()

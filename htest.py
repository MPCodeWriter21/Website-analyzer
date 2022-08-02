import unittest
from main import Handler

obj = Handler()


class TestHandlerFunctions(unittest.TestCase):

    def test_url_checker(self):
        self.assertTrue(url_handler("https://www.google.com"))
        self.assertFalse(url_handler("https;//www.google.com"))
        self.assertTrue(url_handler("google.com"))
        self.assertTrue(url_handler("www.google.com"))

    def test_url_protocol(self):
        self.assertEqual("https", check_protocol("https://www.google.com"))
        self.assertEqual("http", check_protocol("http://www.google.com"))


if __name__ == '__main__':
    unittest.main()

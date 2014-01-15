# !/usr/bin/python


import unittest
import bbot.greet

class TestPyhiGreet(unittest.TestCase):
    def test_hello(self):
        self.assertEquals("Hello, Dave.",
                          bbot.greet.hello())
        self.assertEquals("Hello, Bob.",
                          bbot.greet.hello("Bob"))
        self.assertEquals("Hello, John Doe.",
                          bbot.greet.hello(second="Doe", first="John"))
    def test_goodbye(self):
        self.assertEquals("Goodbye.",
                          bbot.greet.goodbye())

# conditional runs tests if this file called as script (allows import w/o run)
if __name__ == '__main__':
    unittest.main()


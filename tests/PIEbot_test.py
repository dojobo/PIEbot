#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest

import PIEbot

# to run, from root dir:
# python -m pytest tests/

class PIEbotTest(unittest.TestCase):
    def test_basic_tweet(self):
        row = {'root': '*bʰer-', 
            'root_pokorny': '5. bher-', 
            'root_meaning': 'shining; bright brown', 
            'lang_name': bytearray(b'Danish'), 
            'lang_flag': bytearray(b'\xf0\x9f\x87\xa9\xf0\x9f\x87\xb0'), 
            'mod_word': 'bruun', 
            'mod_pos': 'adj', 
            'mod_meaning': 'brown'}
        expected = 'PIE *bʰer- or 5. bher- (shining; bright brown) > Danish "bruun" (adj, "brown")'
        p = PIEbot.PIEbot()
        self.assertEqual(expected, p.write_basic_tweet(row))


    def test_basic_english_tweet(self):
        # shouldn't have an English gloss
        row = {'root': '*peḱ-', 
            'root_pokorny': '1. pek̑-, pēk̑-, pōk̑-', 
            'root_meaning': 'to be joyful, make pretty', 
            'lang_name': bytearray(b'English'), 
            'lang_flag': bytearray(b'\xf0\x9f\x87\xac\xf0\x9f\x87\xa7'), 
            'mod_word': 'fain', 
            'mod_pos': 'adj', 
            'mod_meaning': 'fain'}
        expected = 'PIE *peḱ- or 1. pek̑-, pēk̑-, pōk̑- (to be joyful, make pretty) > English "fain" (adj)'

        p = PIEbot.PIEbot()
        self.assertEqual(expected, p.write_basic_tweet(row))


    def test_basic_pokorny_matches_root(self):
        # don't use "or" in root description if Pokorny matches
        row = {'root': '*bʰer-', 
            'root_pokorny': 'bʰer-', 
            'root_meaning': 'shining; bright brown', 
            'lang_name': bytearray(b'Danish'), 
            'lang_flag': bytearray(b'\xf0\x9f\x87\xa9\xf0\x9f\x87\xb0'), 
            'mod_word': 'bruun', 
            'mod_pos': 'adj', 
            'mod_meaning': 'brown'}
        expected = 'PIE *bʰer- (shining; bright brown) > Danish "bruun" (adj, "brown")'
        p = PIEbot.PIEbot()
        self.assertEqual(expected, p.write_basic_tweet(row))
        

    def test_with_flags(self):
        rows = [
            {'root': '*baba-', 'root_pokorny': 'baba-', 'root_meaning': 'babble, babbling, unclear speech', 
            'lang_name': bytearray(b'German'), 'lang_flag': bytearray(b'\xf0\x9f\x87\xa9\xf0\x9f\x87\xaa'), 'mod_word': 'bappeln, bappern', 'mod_pos': 'v', 'mod_meaning': 'to babble'}, 
            {'root': '*baba-', 'root_pokorny': 'baba-', 'root_meaning': 'babble, babbling, unclear speech', 
            'lang_name': bytearray(b'Manx'), 'lang_flag': None, 'mod_word': 'bab(an)', 'mod_pos': 'n', 'mod_meaning': 'baby'}, 
            {'root': '*baba-', 'root_pokorny': 'baba-', 'root_meaning': 'babble, babbling, unclear speech', 
            'lang_name': bytearray(b'Danish'), 'lang_flag': bytearray(b'\xf0\x9f\x87\xa9\xf0\x9f\x87\xb0'), 'mod_word': 'bable', 'mod_pos': 'v', 'mod_meaning': 'to babble'}
        ]
        expected = ("PIE *baba- (babble, babbling, unclear speech):\n"
            "🇩🇪: \"bappeln, bappern\" (v, \"to babble\")\n"
            "Manx: \"bab(an)\" (n, \"baby\")\n"
            "🇩🇰: \"bable\" (v, \"to babble\")")
        p = PIEbot.PIEbot()
        self.assertEqual(expected, p.write_with_flags(rows))


if __name__ == '__main__':
    unittest.main()
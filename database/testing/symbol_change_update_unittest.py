import unittest
import json
import connect
import traceback

from processing.symbol_change_update import main

class SymbolChangeTest(unittest.TestCase):
    @patch("symbol_change_query.load")
    def test_update(self):

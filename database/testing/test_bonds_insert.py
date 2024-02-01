import unittest
from unittest.mock import Mock, MagicMock, patch
import hashlib
from decimal import *
from sqlalchemy import text
import connect
import sys

sys.path.insert(1, '../SMF_Project_2023/database/processing')
from bonds_insert import BondsInsert as bi

# from database.processing.bonds_insert import BondsInsert

class test_bonds_insert(unittest.TestCase):   
    def test_load_output_file(self):
        # Normal Case - Check ouput
        # expected_hash = "b0c7575abde1b61493f7f6ed3899db48"
        # actual_hash = hashlib.md5(bi.load_output_file("../SMF_Project_2023/test_files/static_test_files/static_bonds_30day.json")).hexdigest
        # # Test against expected output
        # self.assertEqual(actual_hash, expected_hash)

        # File not found
        with patch('builtins.open', side_effect=FileNotFoundError("Mocked File Not Found")):
            with self.assertRaises(SystemExit) as cm:
                bi.load_output_file("nonexistent_file.json")

            self.assertEqual(cm.exception.code, 1)

        # Invlaid JSON
        with patch('builtins.open') as mock_open:
            # Cause JSONDecodeError
            mock_open.return_value.__enter__.return_value.read.return_value = "invalid json content"
            
            with self.assertRaises(SystemExit) as cm:
                bi.load_output_file("invalid_json.json")

            self.assertEqual(cm.exception.code, 1)

    # def test_execute_insert(self):
    #     mock_conn = Mock()
    #     test_entry = {'_bond_date': '2024-01-01', '_bond_month1': '1', '_bond_month2': '2', '_bond_month3': '3', '_bond_month6': '6', '_bond_year1': '1', '_bond_year2': '2', '_bond_year3': '3', '_bond_year5': '5', '_bond_year7': '7', '_bond_year10': '10', '_bond_year20': '20', '_bond_year30': '30'}
    #     bond_id = '111'
    #     bi.execute_insert(mock_conn, test_bonds_insert, bond_id)
    #     mock_conn.execute.assert_called_once()


    # def test_bond_id_exists(self):
    #     mock_conn = Mock()
    #     mock_conn.execute.return_value.one_or_none.return_value = (123,)
    #     test_entry = {'_bond_name': 'TestBond'}
    #     # Call the function
    #     result = bi.get_bond_id(test_entry, mock_conn)
    #     # Verify if correct query was executed
    #     mock_conn.execute.assert_called_once_with(text("SELECT bond_id FROM `bonds` WHERE treasuryName = 'TestBond'"))
        
    #     self.assertEqual(result, 123)

    # @patch('bonds_insert.text')
    # def test_get_bond_id(self, mock_text):
    #     mock_connection = MagicMock()
    #     mock_result = MagicMock()
    #     mock_result.one_or_none.return_value = None # Simulate when bond id doesn't exist
    #     mock_result.one.return_value = (42,) #Simulated a generated ID
    #     mock_connection.execute.return_value = mock_result
    #     mock_text.return_value = 'mocked text'

    #     entry = {'_bond_name': 'example_bond'}
    #     bond_id = bi.get_bond_id(entry, mock_connection)

    #     # Expected behaivour
    #     expected_query = "SELECT bond_id FROM `bonds` WHERE treasuryName = 'example_bond'"
    #     mock_connection.execute.assert_called_once_with(mock_text(expected_query))

    #     # Check the returned bond_id
    #     self.assertEqual(bond_id, 42)

if __name__ == '__main__':
    unittest.main(verbosity=2)
        
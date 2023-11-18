import unittest
from unittest import TestCase
import sqlite3
import json
import datetime

class TestRealtimeIndexInsert(TestCase):
    # Create temp database
    conn = sqlite3.connect(':memory:')

    cursor = conn.cursor()

    test_db_path = "./database/testing/test_realtime_index_db.sql"
    fd = open(test_db_path, 'r')
    createQuery = fd.read()
    cursor.executescript(createQuery)

    # loads output data from json
    def load_output_file(path):
        try:
            with open(path, "r") as output_file:
                output_data = json.load(output_file)
            return output_data
        except FileNotFoundError:
            print(f"Output file '{path}' not found.")
            exit(1)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in '{path}'")
            exit(1)
            
    # Load output data
    realtime_data = load_output_file('./test_files/static_test_files/static_index_realtime.json')
    
    def test_index_insert(self):  
        expect_output = [
            (1, '2023-11-16 14:14:00', 4508.24, 0.119, 5.3604, 4511.99, 4487.83, 4607.07, 3764.49, None, 'INDEX', 4497.08, 4502.88, 2502113000, 3708302656),
            (2, '2023-11-16 14:15:59', 14113.673, 0.0697, 9.8369, 14130.448, 14033.791, 14446.55, 10207.47, None, 'INDEX', 14066.9, 14103.836, 4080972000, 4589035625),
            (3, '2023-11-16 14:14:00', 34945.47, -0.1307, -45.7422, 35022.46, 34818.03, 35679.13, 31429.82, None, 'INDEX', 34868.03, 34991.21, 436835917, 306086406),
            (4, '2023-11-16 13:30:09', 2572.97, -0.0514, -1.3225, 2576.6504, 2562.126, 2650.9, 2173.61, None, 'INDEX', 2572.229, 2574.2925, 0, 0),
            (5, '2023-11-16 08:35:29', 7410.97, -1.0143, -75.9399, 7492.84, 7409.4, 8047.1, 7206.8, None, 'INDEX', 7486.91, 7486.91, 0, 701541262)
        ]
        # Insert each entry into mock databse
        index_id = 1
        for entry in self.realtime_data:
            date = datetime.datetime.fromtimestamp(entry["timestamp"])
            price = entry['price']
            change_percentage = entry['changesPercentage']
            change = entry['change']
            day_high = entry['dayHigh']
            day_low = entry['dayLow']
            year_high = entry['yearHigh']
            year_low = entry['yearLow']
            mkt_cap = entry['marketCap']
            exchange = entry['exchange']
            open_price = entry['open']
            prev_close = entry['previousClose']
            volume = entry['volume']
            vol_avg = entry['avgVolume']

            params = (index_id, date, price, change_percentage, change, day_high, day_low, year_high, year_low, mkt_cap, exchange, open_price, prev_close, volume, vol_avg)

            # Execute row insertion
            self.cursor.execute("INSERT INTO `test_realtime_index_values` VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", params)
            index_id += 1

        # Fetch all data from table
        self.cursor.execute("Select * from test_realtime_index_values")
        rows = self.cursor.fetchall()
        count = 0
        #Check if each fetched row matches the expected output
        for row in rows:
            self.assertEqual(row, expect_output[count])
            count += 1

if __name__ == '__main__':
    unittest.main()
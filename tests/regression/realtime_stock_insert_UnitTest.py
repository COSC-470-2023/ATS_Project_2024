import unittest

from ats.database import realtime_stock_insert
from ats.util import db_handler

# realtime_data = [{
#     "_realtime_symbol": "AAPL",
#     "_realtime_name": "Apple Inc.",
#     "_realtime_price": 189.71,
#     "_realtime_changePercent": 0.9042,
#     "_realtime_change": 1.7,
#     "_realtime_dayLow": 188.65,
#     "_realtime_dayHigh": 190.95,
#     "_realtime_yearHigh": 198.23,
#     "_realtime_yearLow": 124.17,
#     "_realtime_mktCap": 2950521639434,
#     "_realtime_exchange": "NASDAQ",
#     "_realtime_volume": 52844718,
#     "_realtime_volAvg": 59038675,
#     "_realtime_open": 189.57,
#     "_realtime_prevClose": 188.01,
#     "_realtime_eps": 6.13,
#     "_realtime_pe": 30.95,
#     "_realtime_earningsAnnouncement": "2024-01-31T00:00:00.000+0000",
#     "_realtime_sharesOutstanding": 15552799744,
#     "_realtime_date": "2023-11-22"
# }]
#
#
# class StockInsertion(unittest.TestCase):
#     def testCompanyChecker(self):
#         with connect.connect() as conn:
#             for entry in realtime_data:
#                 # if an exception is thrown, the test fails
#                 realtime_stock_insert.get_company_id(entry, conn)
#
#     def test_check_keys(self):
#         # mock entry missing a lot of keys
#         entry = {
#             "_realtime_date": "2023-01-01",
#             "_realtime_price": 100.0,
#         }
#
#         # call the function
#         keys = realtime_stock_insert.check_keys(entry)
#
#         # verify that missing keys are assigned a value of None
#         for key, value in keys.items():
#             if key not in entry:
#                 self.assertEqual(value, None)
#
#     def testInsertion(self):
#         with connect.connect() as conn:
#             for entry in realtime_data:
#                 comp_id = realtime_stock_insert.get_company_id(entry, conn)
#                 realtime_stock_insert.execute_insert(conn, entry, comp_id)

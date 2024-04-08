import unittest

from ats.database import company_statements_insert
from ats.util import db_handler

# company_data = [{
#     "_company_symbol": "AAPL",
#     "_company_date": "2023-11-17 13:00:01",
#     "_company_price": 178.72,
#     "_company_beta": 1.286802,
#     "_company_volAvg": 58405568,
#     "_company_mktCap": 2794144143933,
#     "_company_lastDiv": 0.96,
#     "_company_changes": -0.13,
#     "_company_name": "Apple Inc.",
#     "_company_currency": "USD",
#     "_company_cik": "0000320193",
#     "_company_isin": "US0378331005",
#     "_company_cusip": "037833100",
#     "_company_exchangeFullName": "NASDAQ Global Select",
#     "_company_exchange": "NASDAQ",
#     "_company_industry": "Consumer Electronics",
#     "_company_ceo": "Mr. Timothy D. Cook",
#     "_company_sector": "Technology",
#     "_company_country": "US",
#     "_company_fullTimeEmployees": "164000",
#     "_company_phone": "408 996 1010",
#     "_company_address": "One Apple Park Way",
#     "_company_city": "Cupertino",
#     "_company_state": "CA",
#     "_company_zip": "95014",
#     "_company_dcfDiff": 4.15176,
#     "_company_dcf": 150.082,
#     "_company_ipoDate": "1980-12-12",
#     "_company_isEtf": 0,
#     "_company_isActivelyTrading": 1,
#     "_company_isAdr": 0,
#     "_company_isFund": 0
# }]
#
#
# class StockInsertion(unittest.TestCase):
#     def test_check_keys(self):
#         # mock entry missing a lot of keys
#         entry = {
#             "_company_date": "2023-01-01",
#             "_company_price": 100.0,
#         }
#
#         # call the function
#         keys = company_statements_insert.check_keys(entry)
#
#         # verify that missing keys are assigned a value of None
#         for key, value in keys.items():
#             if key not in entry:
#                 self.assertEqual(value, None)
#
#     def testCompanyChecker(self):
#         with connect.connect() as conn:
#             for entry in company_data:
#                 company_statements_insert.get_company_id(entry, conn)
#
#     def testInsertion(self):
#         with connect.connect() as conn:
#             for entry in company_data:
#                 comp_id = company_statements_insert.get_company_id(entry, conn)
#                 company_statements_insert.execute_insert(conn, entry, comp_id)

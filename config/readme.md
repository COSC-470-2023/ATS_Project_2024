<h1>Configuration Explained (WIP)</h1>
<h2>non_api_fields</h2>

```yaml
  non_api_fields:
    date:
      src: timestamp
      mapping: _realtime_date
      input_type: _unix_time
      output_type: _date_time
```
The purpose of the `non_api_fields` is to list source of data, mapping for the internal fields (see below) and finally the types if conversion is necessary.
<br><br>
If `src` is set to null, it should tell the query script that we are to provide data directly rather than pull from another field.
<br><br>
<b>Example</b>:
<br>
The API's field named `timestamp` will be pulled into a field we add, using the common field `_realtime_date`, and also be converted from a unix epoch timestamp to the date time format.
<br>
```yaml
timestamp: 1700168401
```
becomes
```yaml
_realtime_date: "2023-11-16 13:00:01"
```

<h2>Field Mapping (WIP)</h2>
<b>Example output:</b>
<br>

```json
[
  {
    "_realtime_date": "2023-11-17 13:00:01",
    "_realtime_symbol": "AAPL",
    "_realtime_name": "Apple Inc.",
    "_realtime_price": 189.69,
    "_realtime_changePercent": -0.0105,
    "_realtime_change": -0.02,
    "_realtime_dayLow": 188.575,
    "_realtime_dayHigh": 190.38,
    "_realtime_yearHigh": 198.23,
    "_realtime_yearLow": 124.17,
    "_realtime_mktCap": 2950210583439,
    "_realtime_exchange": "NASDAQ",
    "_realtime_volume": 46970852,
    "_realtime_volAvg": 58857157,
    "_realtime_open": 190.25,
    "_realtime_prevClose": 189.71,
    "_realtime_eps": 6.13,
    "_realtime_pe": 30.94,
    "_realtime_earningsAnnouncement": "2024-01-31T00:00:00.000+0000",
    "_realtime_sharesOutstanding": 15552799744
  }
]
```
<br>
[put Explanation of field mapping here]

<h1>Common Fields</h1>
A set of common internal fields that will be used for scripting processes.
<br>
API's and data sources can vary in field names, and the common internal names will be used to map source data fields to recognized fields for the system.
<h2>List of fields</h2>

```
_realtime_name
_realtime_symbol
_realtime_date *
_realtime_price
_realtime_changePercent
_realtime_change
_realtime_dayHigh
_realtime_dayLow
_realtime_yearHigh
_realtime_yearLow
_realtime_mktCap
_realtime_exchange
_realtime_volume
_realtime_volAvg
_realtime_open
_realtime_prevClose
_realtime_eps
_realtime_pe
_realtime_earningsAnnouncement
_realtime_sharesOutstanding

_historical_name *
_historical_symbol
_historical_date
_historical_open
_historical_high
_historical_low
_historical_close
_historical_adjClose
_historical_volume
_historical_unadjustedVolume
_historical_change
_historical_changePercent
_historical_vwap
_historical_changeOverTime

_bond_name *
_bond_date
_bond_month1
_bond_month2
_bond_month3
_bond_month6
_bond_year1
_bond_year2
_bond_year3
_bond_year5
_bond_year7
_bond_year10
_bond_year20
_bond_year30

_company_name
_company_symbol
_company_date
_company_price
_company_beta
_company_volAvg
_company_mktCap
_company_lastDiv
_company_changes
_company_currency
_company_cik
_company_isin
_company_cusip
_company_exchangeFullName
_company_exchange
_company_industry
_company_ceo
_company_sector
_company_country
_company_fullTimeEmployees
_company_phone
_company_address
_company_city
_company_state
_company_zip
_company_dcfDiff
_company_dcf
_company_ipoDate
_company_isEtf
_company_isActivelyTrading
_company_isAdr
_company_isFund

_change_newSymbol
_change_oldSymbol
_change_newName
_change_oldName *
_change_date
```
`*: fields manually added`<br>
`**: N/A`

<h2>List of input and output types for added field conversion</h2>

```
_unix_time
_date_time
_config_name *
_string

_today **
_week_before **
```
`*: types that are config sources`<br>
`**: types that denote date durations for bonds`

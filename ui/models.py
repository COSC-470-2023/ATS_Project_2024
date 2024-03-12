from flask_login import UserMixin
from . import db

db.Model.metadata.reflect(db.engine)

## User Table ##


class Users(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables["users"]


## Bonds Tables ##


class Bonds(db.Model):
    __table__ = db.Model.metadata.tables["bonds"]


class BondValues(db.Model):
    __table__ = db.Model.metadata.tables["bond_values"]


## Commodity Tables ##


class Commodities(db.Model):
    __table__ = db.Model.metadata.tables["commodities"]


class RealtimeCommodityValues(db.Model):
    __table__ = db.Model.metadata.tables["realtime_commodity_values"]


class HistoricalCommodityValues(db.Model):
    __table__ = db.Model.metadata.tables["historical_commodity_values"]


## Company/Stock Tables ##


class Companies(db.Model):
    __table__ = db.Model.metadata.tables["companies"]


class CompanyStatements(db.Model):
    __table__ = db.Model.metadata.tables["company_statements"]


class RealtimeStockValues(db.Model):
    __table__ = db.Model.metadata.tables["realtime_stock_values"]


class HistoricalStockValues(db.Model):
    __table__ = db.Model.metadata.tables["historical_stock_values"]


## Index Tables ##


class Indexes(db.Model):
    __table__ = db.Model.metadata.tables["indexes"]


class RealtimeIndexValues(db.Model):
    __table__ = db.Model.metadata.tables["realtime_index_values"]


class HistoricalIndexValues(db.Model):
    __table__ = db.Model.metadata.tables["historical_index_values"]

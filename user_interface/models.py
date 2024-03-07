from flask_login import UserMixin
from . import db

db.Model.metadata.reflect(db.engine)

## User Table ##


class Users(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables["authorized_users"]


## Bonds Tables ##


class Bonds(db.Model):
    __table__ = db.Model.metadata.tables["bonds"]

    def __repr__(self):
        return self.DISTRICT


class BondValues(db.Model):
    __table__ = db.Model.metadata.tables["bond_values"]

    def __repr__(self):
        return self.DISTRICT


## Commodity Tables ##


class Commodities(db.Model):
    __table__ = db.Model.metadata.tables["commodities"]

    def __repr__(self):
        return self.DISTRICT


class RealtimeCommodityValues(db.Model):
    __table__ = db.Model.metadata.tables["realtime_commodity_values"]

    def __repr__(self):
        return self.DISTRICT


class HistoricalCommodityValues(db.Model):
    __table__ = db.Model.metadata.tables["historical_commodity_values"]

    def __repr__(self):
        return self.DISTRICT


## Company/Stock Tables ##


class Companies(db.Model):
    __table__ = db.Model.metadata.tables["companies"]


class CompanyStatements(db.Model):
    __table__ = db.Model.metadata.tables["company_statements"]

    def __repr__(self):
        return self.DISTRICT


class RealtimeStockValues(db.Model):
    __table__ = db.Model.metadata.tables["realtime_stock_values"]


class HistoricalStockValues(db.Model):
    __table__ = db.Model.metadata.tables["historical_stock_values"]

    def __repr__(self):
        return self.DISTRICT


## Index Tables ##


class Indexes(db.Model):
    __table__ = db.Model.metadata.tables["indexes"]

    def __repr__(self):
        return self.DISTRICT


class RealtimeIndexValues(db.Model):
    __table__ = db.Model.metadata.tables["realtime_index_values"]

    def __repr__(self):
        return self.DISTRICT


class HistoricalIndexValues(db.Model):
    __table__ = db.Model.metadata.tables["historical_index_values"]

    def __repr__(self):
        return self.DISTRICT

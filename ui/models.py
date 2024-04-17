from flask_login import UserMixin
from sqlalchemy.orm import relationship
from . import db

db.Model.metadata.reflect(db.engine)

"""
Defines ORM models for various database tables using SQLAlchemy and Flask-Login's UserMixin.

This module reflects the existing database schema into SQLAlchemy ORM models, allowing for easy
interaction with the database tables. Each model class is derived from a base model which includes
a method for serializing its attributes into a dictionary. This setup allows JSON conversion in a Flask application.

Classes:
- BaseModel: An abstract base class to provide serialization.
- User: records from the 'users' table.
- Bonds, BondValues: records from 'bonds' and 'bond_values' tables.
- Commodities, RealtimeCommodityValues, HistoricalCommodityValues: records from 'commodities' table.
- Companies, CompanyStatements, RealtimeStockValues, HistoricalStockValues: records from tables related to 'companies'.
- Indexes, RealtimeIndexValues, HistoricalIndexValues: records from 'indexes' tables.
"""


class BaseModel(db.Model):

    __abstract__ = True

    def serialize(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


# User Table #


class User(BaseModel, UserMixin):
    __table__ = db.Model.metadata.tables["users"]


# Bonds Tables #


class Bonds(BaseModel):
    __table__ = db.Model.metadata.tables["bonds"]


class BondValues(BaseModel):
    __table__ = db.Model.metadata.tables["bond_values"]


# Commodity Tables #


class Commodities(BaseModel):
    __table__ = db.Model.metadata.tables["commodities"]


class RealtimeCommodityValues(BaseModel):
    __table__ = db.Model.metadata.tables["realtime_commodity_values"]


class HistoricalCommodityValues(BaseModel):
    __table__ = db.Model.metadata.tables["historical_commodity_values"]


# Company/Stock Tables #


class Companies(BaseModel):
    __table__ = db.Model.metadata.tables["companies"]
    # Define relationships
    company_statements = relationship("CompanyStatements", back_populates="company")
    realtime_stock_values = relationship(
        "RealtimeStockValues", back_populates="company"
    )
    historical_stock_values = relationship(
        "HistoricalStockValues", back_populates="company"
    )


class CompanyStatements(BaseModel):
    __table__ = db.Model.metadata.tables["company_statements"]
    # Define relationships
    company = relationship("Companies", back_populates="company_statements")


class RealtimeStockValues(BaseModel):
    __table__ = db.Model.metadata.tables["realtime_stock_values"]
    # Define relationships
    company = relationship("Companies", back_populates="realtime_stock_values")


class HistoricalStockValues(BaseModel):
    __table__ = db.Model.metadata.tables["historical_stock_values"]
    # Define relationships
    company = relationship("Companies", back_populates="historical_stock_values")


# Index Tables #


class Indexes(BaseModel):
    __table__ = db.Model.metadata.tables["indexes"]


class RealtimeIndexValues(BaseModel):
    __table__ = db.Model.metadata.tables["realtime_index_values"]


class HistoricalIndexValues(BaseModel):
    __table__ = db.Model.metadata.tables["historical_index_values"]

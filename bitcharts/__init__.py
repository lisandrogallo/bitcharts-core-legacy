#-*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import date, datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/bitcharts.db'
db = SQLAlchemy(app)


class Currency(db.Model):
    __tablename__ = "currencies"

    id = db.Column(db.Integer, db.Sequence('currency_id_seq'), primary_key=True)
    name = db.Column(db.String(10), unique=True)
    description = db.Column(db.String)
    cryptocurrency = db.Column(db.Boolean)
    active = db.Column(db.Boolean)

    def __init__(self, name, description, cryptocurrency, active):
        self.name = name
        self.description = description
        self.cryptocurrency = cryptocurrency
        self.active = active

#     def __repr__(self):
#         return '<Currency %r>' % self.name


class Exchange(db.Model):
    __tablename__ = "exchanges"

    id = db.Column(db.Integer, db.Sequence('exchange_id_seq'), primary_key=True)
    name = db.Column(db.String(10))
    country = db.Column(db.String(10))
    url = db.Column(db.String)
    api = db.Column(db.String)
    currency_id = db.Column(db.Integer, db.ForeignKey("currencies.id"))
    currency = db.relationship(
        "Currency",
    backref=db.backref("exchanges", order_by=id))
    active = db.Column(db.Boolean)

    def __init__(self, name, country, url, api, currency_id, active):
        self.name = name
        self.country = country
        self.url = url
        self.api = api
        self.currency_id = currency_id
        self.active = active


class Association(db.Model):
    __tablename__ = 'exchanges_currencies'

    id = db.Column(db.Integer, db.Sequence('association_id_seq'), primary_key=True)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchanges.id'))
    currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'))
    last = db.Column(db.Float)
    date = db.Column(db.Date, default=date.today())
    time = db.Column(db.Time, default=datetime.now().time())

#
#     def asdict(self, session):
#         """
#         Function which returns an ordered dictionary containing field values
#         from the current Association object.
#         """
#         properties = OrderedDict()
#
#         id = self.exchange_id
#         exchange = session.query(Exchange).filter(Exchange.id == id).first()
#         properties['display_URL'] = exchange.url
#         properties['display_name'] = exchange.name
#         properties['currency'] = exchange.currency.name
#
#         if exchange.currency.name == 'ARS':
#             properties['blue'] = self.last
#         else:
#             properties['last'] = self.last
#
#         return exchange.name.lower(), properties

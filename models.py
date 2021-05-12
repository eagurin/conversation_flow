import os
import sys

from dotenv import load_dotenv
from sqlalchemy import (Column, Float, ForeignKey, Integer, String,
                        create_engine)
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

sys.path.append("..")
load_dotenv()

Base = declarative_base()
Session = sessionmaker()

config = dict(
    drivername=os.environ.get("DB_DRIVER"),
    username=os.environ.get("DB_USERNAME"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT"),
    database=os.environ.get("DB_NAME"),
    query={'charset': 'utf8mb4'}
)
url = URL(**config)

try:
    engine = create_engine(url, echo=False)
except:
    engine = create_engine('sqlite://', echo=False)
finally:
    Session.configure(bind=engine)
    session = Session()


class Order(Base):
    __tablename__ = 'oc_order'

    order_id = Column(Integer, primary_key=True)
    track_no = Column(String)
    customer_id = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    telephone = Column(String)
    shipping_method = Column(String)
    comment = Column(String)
    total = Column(Float)
    order_status_id = Column(Integer)
    language_id = Column(Integer)
    currency_id = Column(Integer)
    order_status = relationship("OrderStatus", backref="oc_order", order_by="OrderStatus.order_status_id")

    def __repr__(self):
            return "<Order(%r, %r)>" % (self.order_id, self.order_status)


class OrderStatus(Base):
    __tablename__ = 'oc_order_status'

    order_status_id = Column(ForeignKey('oc_order.order_status_id'), primary_key=True)
    language_id = Column(Integer)
    name = Column(String)

    def __repr__(self):
        return str(self.name)


class Customer(Base):
    __tablename__ = 'oc_customer'

    customer_id = Column(Integer, primary_key=True)
    firstname = Column(String)
    lastname = Column(String)
    telephone = Column(String)
    email = Column(String)

    def __repr__(self):
        return str(self.firstname) + ' ' + str(self.orders) 

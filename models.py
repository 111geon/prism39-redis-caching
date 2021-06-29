from sqlalchemy import Column, Integer, DateTime, Numeric

from database   import Base


class TestData1(Base):
    __tablename__ = 'test_data_1'
    index         = Column(Integer, primary_key=True, index=True)
    listingid     = Column(Integer)
    date          = Column(DateTime)
    value         = Column(Numeric(12,8))



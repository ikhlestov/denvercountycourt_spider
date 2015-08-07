from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine, Column, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base

import settings

DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    engine = create_engine(URL(**settings.DATABASE), echo=False)
    return engine


def create_deals_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class ScheduleBase(DeclarativeBase):
    __tablename__ = 'schedule_items'

    id = Column(Integer, primary_key=True)
    case_number = Column('case_number', String(255), nullable=True)
    defendant = Column('defendant', String(255), nullable=True)
    disposition = Column('disposition', String(255), nullable=True)
    next_courtroom = Column('next_courtroom', String(255), nullable=True)
    next_cort_date = Column('next_cort_date', String(255), nullable=True)  ## maybe use date here??
    meeting_title = Column('meeting_title', String(255), nullable=True)

class CaseBase(DeclarativeBase):
    __tablename__ = 'case_items'

    id = Column(Integer, primary_key=True)
    case_number = Column('case_number', String(255), nullable=True)
    html_body = Column('html_body', Text(), nullable=True)

class HistoricBase(DeclarativeBase):
    __tablename__ = 'historic_items'

    id = Column(Integer, primary_key=True)
    courtroom_date = Column('courtroom_date', String(255), nullable=True)
    courtroom = Column('courtroom', String(255), nullable=True)

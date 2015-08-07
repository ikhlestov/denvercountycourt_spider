# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker

from models import ScheduleBase, CaseBase, HistoricBase, \
    db_connect, create_deals_table
from items import ScheduleItem, CaseItem, HistoricItem

class DenvercountycourtPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates tables.
        """
        engine = db_connect()
        create_deals_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        if isinstance(item, ScheduleItem):
            database_item = ScheduleBase(
                case_number=item.get('case_number', ''),
                defendant=item.get('defendant', ''),
                disposition=item.get('disposition', ''),
                next_courtroom=item.get('next_courtroom', ''),
                next_cort_date=item.get('next_cort_date', ''),
                meeting_title=item.get('meeting_title', ''),
            )
        if isinstance(item, CaseItem):
            database_item = CaseBase(
                case_number=item.get('case_number', ''),
                html_body=item.get('html_body', ''),
            )
        if isinstance(item, HistoricItem):
            database_item = HistoricBase(
                courtroom_date=item.get('courtroom_date', ''),
                courtroom=item.get('courtroom', ''),
            )
        session.add(database_item)
        session.commit()
        return item

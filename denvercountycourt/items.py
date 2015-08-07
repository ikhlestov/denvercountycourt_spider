# -*- coding: utf-8 -*-
from scrapy import Item, Field


class ScheduleItem(Item):
    case_number = Field()
    defendant = Field()
    disposition = Field()
    next_courtroom = Field()
    next_cort_date = Field()
    meeting_title = Field()  # identified by the h3 title above each section of search results

class CaseItem(Item):
    case_number = Field()
    html_body = Field()  # beginning with <h3>Case Information</h3> and ending just before <div id="sidebar-default_sidebar"

class HistoricItem(Item):
    courtroom_date = Field()
    courtroom = Field()

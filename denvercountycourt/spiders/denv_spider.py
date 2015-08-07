# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from urlparse import urlparse, parse_qs
import re

import scrapy
import requests
from scrapy.http import FormRequest, Request
from scrapy.utils.response import open_in_browser
from sqlalchemy.orm import sessionmaker

from denvercountycourt.settings import CAPTCHA_USERNAME, CAPTHCA_PASSWORD
from denvercountycourt.items import ScheduleItem, CaseItem, HistoricItem
from denvercountycourt.models import ScheduleBase, CaseBase, HistoricBase,\
    db_connect, create_deals_table
from dbc import SocketClient, MySocketClient


DEFAULT_TIMEOUT = 60

cond_set_value = lambda y, default=0: y[0] if y else default

def generate_historic_mode_date_list():
    d1 = date(1986, 1, 1)
    date_now = datetime.now()
    d2 = date(date_now.year, date_now.month, date_now.day)
    delta = d2 - d1
    generator = (d1 + timedelta(days=i) for i in range(delta.days + 1))
    return generator

def generate_update_mode_date_list():
    today = datetime.now()
    days = []
    for i in reversed(range(1, 4)):
        another_day = today - timedelta(days=i)
        days.append(another_day)
    days.append(today)
    for i in range(1, 8):
        another_day = today + timedelta(days=i)
        days.append(another_day)
    # remove holidays
    days = [d for d in days if d.weekday() < 5]
    # change to strings
    days = [d.strftime('%m/%d/%Y') for d in days]
    return days


class DenvSpiderSpider(scrapy.Spider):
    name = "denv_spider"
    allowed_domains = ["www.denvercountycourt.org"]
    start_urls = (
        'https://www.denvercountycourt.org/search/?searchtype=searchdocket',
    )

    search_url = "https://www.denvercountycourt.org/search"

    countroom_url = "https://www.denvercountycourt.org/search/?"\
    "searchtype=searchdocket&date={date}&room={room}&token={token}"

    captcha_was_requested = False

    token = None

    delayed_tuples = []

    rooms = [
        "100K",
        "100KN",
        "104",
        "104BN",
        "105A",
        "105AN",
        "159",
        "164",
        "175",
        "186",
        "2100",
        "2300",
        "3A",
        "3B",
        "3C",
        "3D",
        "3E",
        "3F",
        "3G",
        "3H",
        "4A",
        "4C",
    ]
    def __init__(self, update_mode=False, historic_mode=False,
                 *args, **kwargs):
        self.days = None
        self.update_mode = True
        if historic_mode:
            self.mode = 'historic_mode'
            self.days = generate_historic_mode_date_list()
            self.update_mode = False
        else:
            self.mode = 'udpate_mode'
            self.days = generate_update_mode_date_list()  ##############DEBUG LIMIT!!!!!!!!!!
        super(DenvSpiderSpider, self).__init__(*args, **kwargs)
        self.days_generator = self.create_generator()
        self.logger.info("'%s' mode was on", self.mode)

        # create connect to MySQL database
        engine = db_connect()
        create_deals_table(engine)
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def create_generator(self):
        for date in self.days:
            for room in self.rooms:
                yield (date,room)

    def parse(self, response):
        if response.meta.get('return_capthca_was_requested_to_false'):
            self.captcha_was_requested = False
        captcha_url = response.xpath('.//img[@id="cimage"]/@src').extract()
        if captcha_url:
            if not self.captcha_was_requested:
                return self.create_captcha_request(response)

    def send_request_with_token(self, response):
        if response.meta.get('return_capthca_was_requested_to_false'):
            self.captcha_was_requested = False
        captcha_url = response.xpath('.//img[@id="cimage"]/@src').extract()
        if captcha_url:
            if not self.captcha_was_requested:
                return self.create_captcha_request(response)
        else:
            token_url = response.xpath(
                './/td[@class="case_no"]/a/@href').extract()
            if token_url:
                token_url = token_url[0]
                q = urlparse(token_url).query
                token = parse_qs(q)['token'][0]
                self.token = token
                return self.generate_requests_with_token()
            else:
                self.logger.error("Captcha token was not found!")

    def generate_requests_with_token(self):
        token = self.token
        try:
            d_t_tuple = next(self.days_generator)
        except Exception as e:
            print(e)
            print("GENERATOR WAS EMPTY")
            print("!"*100)
            try:
                d_t_tuple = self.delayed_tuples.pop()
            except Exception as e:
                print e
                print("!"*100)
                d_t_tuple = None
        if d_t_tuple:
            date, room = d_t_tuple
            # check if request for that page were made already sometimes
            if not self.update_mode:
                query = self.session.query(HistoricBase).filter(
                    HistoricBase.courtroom_date == date,
                    HistoricBase.courtroom == room,
                )
                # request was this room was performed sometimes
                if query.count() != 0:
                    return self.generate_requests_with_token()

            meta = {'d_t_tuple': d_t_tuple}
            url = self.countroom_url.format(
                date=date,
                room=room,
                token=token,
            )
            print("SEND REQUEST TO ROOM")
            print(url)
            return Request(url=url, callback=self.parse_results,
                          meta=meta, dont_filter=True, priority=-3)

    def create_captcha_request(self,response):
        self.captcha_was_requested = True
        captcha_url = response.xpath('.//img[@id="cimage"]/@src').extract()
        captcha_url = captcha_url[0]
        meta = {'captcha_url': captcha_url,
                'return_capthca_was_requested_to_false': True}
        return Request(captcha_url, callback=self.handle_captcha,
                      meta=meta, priority=5)

    def handle_captcha(self, response):
        form_data = {
            'searchtype':'searchdocket',
            'date':'05/07/2015',
            'room':'100K',
            'search':'Search',
        }
        client = MySocketClient(CAPTCHA_USERNAME, CAPTHCA_PASSWORD)
        client.is_verbose = True
        captcha_image = response.body
        captcha = client.decode(captcha_image, DEFAULT_TIMEOUT)
        captcha_text = captcha["text"]
        form_data['code'] = captcha_text
        yield FormRequest(url=self.search_url, formdata=form_data,
                          callback=self.send_request_with_token,
                          meta=response.meta.copy(),
                          priority=5)

    def parse_results(self, response):
        x = r"input\[name='code'\]"
        captcha_url = response.xpath('.//img[@id="cimage"]/@src').extract()
        if captcha_url:
            error_capthca_text = re.findall(x, response.body)
            if error_capthca_text:
                print("captcha was enterd incorect")
                # captcha was entered incorect, try again
                if not self.captcha_was_requested:
                    yield self.create_captcha_request(response)
                self.delayed_tuples.append(response.meta.get('d_t_tuple'))
            else:
                d_t_tuple = response.meta.get('d_t_tuple')
                h_item = self.generate_historic_item(d_t_tuple)
                yield h_item
                yield self.generate_requests_with_token()
        else:
            d_t_tuple = response.meta.get('d_t_tuple')
            h_item = self.generate_historic_item(d_t_tuple)
            yield h_item

            item_links = response.xpath('.//td[@class="case_no"]/a')
            for link in item_links[:5]: ##############DEBUG LIMIT!!!!!!!!!!
                link_name = cond_set_value(link.xpath('.//text()').extract())
                link_url = cond_set_value(link.xpath('.//@href').extract())
                meta = {'link_name': link_name,
                        'link_url': link_url}
                yield Request(link_url, callback=self.parse_item, priority=-2,
                              meta=meta)

            # get items
            table_trs = response.xpath('.//table[@class="case_results"]/tr')
            print table_trs
            meeting_title = ''
            for tr in table_trs[1:]:
                text = tr.xpath('.//td[@colspan="5"]/h3/text()').extract()
                if text:
                    meeting_title = text[0]
                else:
                    s_item = ScheduleItem()
                    s_item['meeting_title'] = meeting_title
                    s_item['case_number'] = cond_set_value(
                        tr.xpath('.//td[@class="case_no"]/a/text()').extract())
                    s_item['defendant'] = cond_set_value(
                        tr.xpath('.//td[@class="defendant"]/text()').extract())
                    s_item['disposition'] = cond_set_value(
                        tr.xpath('.//td[@class="disposition"]/text()').extract())
                    s_item['next_courtroom'] = cond_set_value(
                        tr.xpath('.//td[@class="courtroom"]/text()').extract())
                    s_item['next_cort_date'] = cond_set_value(
                        tr.xpath('.//td[@class="date"]/text()').extract())
                    yield s_item

            yield self.generate_requests_with_token()

    def parse_item(self, response):
        link_name = response.meta.get('link_name')
        link_url = response.meta.get('link_url')
        captcha_url = response.xpath('.//img[@id="cimage"]/@src').extract() 
        if captcha_url:
            print("captcha at parse item\n")
            # captcha was entered incorect, try again
            if not self.captcha_was_requested:
                yield self.create_captcha_request(response)
                yield Request(url=link_url, dont_filter=True,
                              priority=-2, meta=response.meta.copy())
        print("all is ok at parse item")
        c_item = CaseItem()
        c_item['case_number'] = link_name
        c_item['html_body'] = cond_set_value(re.findall(r'(<h3>Case Information.*)<aside', response.body, re.DOTALL))
        yield c_item

    def generate_historic_item(self, d_t_tuple):
        date, room = d_t_tuple
        h_item = HistoricItem()
        h_item['courtroom_date'] = date
        h_item['courtroom'] = room
        self.logger.info("no any results for {date}:{room}".format(date=date, room=room))
        return h_item
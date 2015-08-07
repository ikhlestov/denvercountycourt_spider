# -*- coding: utf-8 -*-
import os


BOT_NAME = 'denvercountycourt'

SPIDER_MODULES = ['denvercountycourt.spiders']
NEWSPIDER_MODULE = 'denvercountycourt.spiders'

DOWNLOAD_HANDLERS = {
  's3': None,
}
DUPEFILTER_DEBUG = True

ITEM_PIPELINES = {
    'denvercountycourt.pipelines.DenvercountycourtPipeline': 300,
}

CAPTCHA_USERNAME = os.getenv('CAPTCHA_USERNAME')
CAPTHCA_PASSWORD = os.getenv('CAPTHCA_PASSWORD')

DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')

DATABASE = {
    'drivername': 'mysql',
    'host': 'coloradorecords.c5bnots1acia.us-east-1.rds.amazonaws.com',
    # 'host': 'localhost',
    'port': '3306',
    'username': DATABASE_USERNAME,
    'password': DATABASE_PASSWORD,
    'database': 'coloradorecords',
    'query': {
        'charset': 'utf8',
    }
}

try:
    from settings_local import *
except:
    pass

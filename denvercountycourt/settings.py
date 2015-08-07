# -*- coding: utf-8 -*-
import os


BOT_NAME = 'denvercountycourt'

SPIDER_MODULES = ['denvercountycourt.spiders']
NEWSPIDER_MODULE = 'denvercountycourt.spiders'

DOWNLOAD_HANDLERS = {
  's3': None,
}
DUPEFILTER_DEBUG = True
# CONCURRENT_REQUESTS_PER_DOMAIN = 1

ITEM_PIPELINES = {
    'denvercountycourt.pipelines.DenvercountycourtPipeline': 300,
}

CAPTCHA_USERNAME = os.getenv('CAPTCHA_USERNAME')
CAPTHCA_PASSWORD = os.getenv('CAPTHCA_PASSWORD')

try:
    from settings_local import *
except:
    pass

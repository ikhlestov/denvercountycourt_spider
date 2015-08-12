#Spider for https://www.denvercountycourt.org

Spider was build with [Python 2.7](https://www.python.org/) [Scrapy](http://scrapy.org/) framework. It store results in MySQL database through [SQLAlchemy](http://www.sqlalchemy.org/) framework.
Spider will fetch the site for room/meetings within required dates.
Site display the captchas for search results but with right credentials for deapthbycaptha they should be solved.
If spider fail to solve capthca from first attempt it will try more times.

## Installation

1. Clone the repo
2. Install all requirements
3. Provide you credentials for the database connection and deathbycaptcha service to environment or to `settings_local.py`(you should create this file near main `settings.py` file)

## Usage

There two available modes for spider:

1. **Update mode.**
Spider will get all results for past 3 days, today, and next 7 days not including holidays.
Command to run: `scapy crawl denv_spider -a update_mode=True`
This is default mode, so you may just try `scapy crawl denv_spider`

2. **Historic mode.**
Spider will get all info from 1986 till today not including holidays.
Command to run: `scapy crawl denv_spider -a historic_mode=True`
It may spend a lot time/coast to finish so be sure when run in this mode.

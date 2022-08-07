#%%
import io
import os
import boto3

from tempfile import mkdtemp
from bs4 import BeautifulSoup
import requests as re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from selenium import webdriver
from time import sleep
from re import search

import pandas as pd
import numpy as np

class webScraper:
    '''The superclass validates the input choices and controls common functions across scrapers'''
    def __init__(self, scrape_type, links=None):
        self.scrape_type = scrape_type
        self.description = None
        self.pipeline = None

        if scrape_type == 'html':
            if links is not None: 
                raise TypeError("html does accept direct download links. Change type to direct_download or delete links.")
            print('html set')

        elif scrape_type == 'dynamic_content':
            if links is not None: 
                raise TypeError("dynamic_content cannot accept direct download links. Change type to direct_download or delete links.")
            print('dynamic_content set')

        elif scrape_type == 'direct_download':
            self.attributes = links
            if links == None:
                raise TypeError('download links not provided to type direct_download')
        else: 
            raise TypeError('Not a supported scrape type. Allowed types: direct_download, html, dynamic_content')

    def pipeline(self):
        '''runs a user defined data processing pipeline to parse the text from the scrape'''
        data = self.pipeline(self.soup)
        return data

class scrapeHTML(webScraper):
    '''scrapeHTML scrapes a static site for html content'''
    def __init__(self, params, links=None):
        super(scrapeHTML, self).__init__(scrape_type='html', links=links)
        self.description = params['description']
        self.site_url = params['site_url'] # Site url for data
        self.base_url = params['base_url'] # base url for downloads if different than site url
        self.find = params['find'] # parameter to find in the html 
        self.href = params['href'] # whether or not to look for href tags (links)
        self.attributes = [] # retrieved attributes from html
        self.pipeline = params["pipeline"] # data processing function to use

    def get_html(self):
        ''' this function returns a soup of html from a static website'''
        print('Getting HTML...')
        # set up session for retry handling
        session = re.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        r = re.get(self.site_url)
        soup = BeautifulSoup(r.content)
        print('HTML retrieved.')
        self.soup = soup
        return self

    def get_links(self):
        '''this function returns a list of href tagged links from the soup'''
        atts = []
        for att in self.soup.findAll(self.find['tag'], href=self.href):
            if all(x in att.get(self.find['attribute']) for x in self.find['statements']):
                if self.base_url is not None:
                    atts.append(self.base_url+att.get(self.find['attribute']))
                else:
                    atts.append(self.site_url+att.get(self.find['attribute']))
            else:
                continue
        print('Attributes retrieved from HTML.')
        self.attributes = atts

        return self

class scrapeDynamicContent(webScraper):
    '''scrapeDynamicContent uses the selenium library and headless chrome to scrape dynamic content from javascript'''
    def __init__(self, params, links=None):
        super(scrapeDynamicContent, self).__init__(scrape_type='dynamic_content', links=links)
        self.description = params['description']
        self.site_url = params['site_url'] # Site url for data
        self.href = params['href'] # whether or not to look for href tags (links)
        self.attributes = [] # retrieved attributes from html
        self.pipeline = params['pipeline']

    def set_chrome(self):
        '''sets headless chrome options for Selenium and returns a webdriver'''
        options = webdriver.ChromeOptions()
        options.binary_location = '/opt/chrome/chrome'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9222")
        chrome = webdriver.Chrome("/opt/chromedriver",
                                options=options)

        return chrome

    def get_dynamic_content(self):
        '''gets web content via Selenium and loads it to BeautifulSoup for parsing'''
        driver = self.set_chrome()
        driver.get(self.site_url)
        sleep(20) # make sure dynamic content has loaded
        print('web page scraping complete')
        self.soup = BeautifulSoup(driver.page_source)
        return self

class directDownload(webScraper):
    '''directDownload accepts a list of links to download and returns a dictionary with a json of the data included'''
    def __init__(self, params, links=None):
        super(directDownload, self).__init__(scrape_type='direct_download', links=links)
        self.description = params['description']
        self.site_url = params['site_url'] # Site url for data
        self.href = params['href'] # whether or not to look for href tags (links)
        self.pipeline = params['pipeline']
        if links is not None:
            self.attributes = links # retrieved attributes from html
        else: print('Warning! You have not provided a list of links to directDownload. Set attributes using obj.attributes')
    
    def get_downloads(self):
        '''download files at provided links'''
        session = re.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        content = {}
        for link in self.links:
            r = re.get(link)
            if r.status_code == 200:
                content[link] = r.json
    
        return content
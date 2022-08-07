
#%%
import scrapeit.scrapers as scrapeit
from pipelines.bih_processor import get_info

def handler(event, context):
    
    scraper = scrapeit.scrapeHTML(event)
    scraper = scraper.get_html()
    links = scraper.get_links().attributes
    values = scraper.pipeline(get_info)

    return links, values
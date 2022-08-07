#%%
from bs4 import BeautifulSoup

def get_info(soup):
    '''this function gets data from http://example.python-scraping.com/places/default/view/Bosnia-and-Herzegovina-29'''
    labels = []
    data = []
    for label in soup.findAll('label'):
        labels.append(label.text)
    table = soup.find('table')
    values = []
    for child in table.findChildren('td'):
        values.append(child.text)
    values = [x for x in values if x not in labels]
    values = [x for x in values if x!='']
    values.insert(0,'flag')
    labels = [x.replace(': ','') for x in labels]
    
    return dict(zip(labels, values))
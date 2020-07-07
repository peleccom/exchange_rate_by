from decimal import Decimal
import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent


AVAILAIBLE_CURRENCIES = [
    'usd',
    'eur',
    'rub100',
]

CITY = 'minsk'

class ExchangeRate:
    def __init__(self, buy, sell):
        self.buy = buy
        self.sell = sell

def get_rates(currency):
    if currency not in AVAILAIBLE_CURRENCIES:
        raise ValueError(f'invalid currency code {currency}')
        
    result = []        
    url = f'https://myfin.by/currency/{CITY}'
    headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}        
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    
    best_rates_table = soup.body.find('div', class_='best-rates').find('table')
    
    best_rates_rows = best_rates_table.find('tbody').find_all('tr')
    nbrb_bank_name = 'НБ РБ'
    for best_rates_row in best_rates_rows:
        cells = best_rates_row.find_all('td')
        best_rates_currency = cells[0].find('a', href=True)['href'].replace('/currency/','')
        if (currency == 'rub100' and best_rates_currency== 'rub') or (best_rates_currency == currency):
            result.append(dict(name=nbrb_bank_name, rate=ExchangeRate(Decimal(cells[3].text), Decimal(0))))
    rates_table = soup.body.find('div', class_='page_currency').find('table', class_ = 'rates-table-sort')
    
    cols = rates_table.find('thead').find_all('th', class_='cur-name')
    currencies = []
    for col in cols:
        currencies.append(col.text)
    
    bank_lines = rates_table.find_all('tr', class_='tr-tb')
    col_index = currencies.index(currency)
    if col_index == -1:
       raise ValueError(f'invalid currency code {currency}')

    for bank_line in bank_lines:
        cells = bank_line.find_all('td')
        bank_name = cells[0].text.strip()
        buy = Decimal(cells[1 + col_index * 2].text)
        sell = Decimal(cells[1 + col_index * 2 + 1].text)
        result.append(dict(name=bank_name, rate=ExchangeRate(buy, sell)))
    return result
        
     
rows = get_rates('usd')
for row in rows:
    name = row['name']
    rate = row['rate']
    print(name, rate.buy, rate.sell)
   
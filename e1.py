#!/usr/bin/env python

import urllib.request
from bs4 import BeautifulSoup

url_base = "http://www.portaldatransparencia.gov.br/PortalComprasDiretasOEOrgaoSuperior.asp?Ano=%d&Valor=86726995548647&Pagina=%d"
year = 2015
total = 0
items = []


for i in range(1, 3):
    url = url_base % (year, i)
    html = urllib.request.urlopen(url).read().decode('iso-8859-1')
    soup = BeautifulSoup(html, 'html.parser')

    if i == 1:
        total = soup.find(id='totais').find(class_='colunaValor').text.strip()

    rows = soup.find(id='listagem').find_all('tr')
    for r in rows[1:]:
        _, name, value = r.find_all('td')
        items.append((name.text.strip(), value.text.strip()))


s = '%-50s%20s'
print('Total destinado pelo Governo federal em %d: R$ %s' % (year, total))
print(s % ('Órgão', 'Total no ano (R$)'))
for i in items:
    print(s % i)

import os
import requests
from bs4 import BeautifulSoup

pdfs = []

response = requests.get('http://frequencyplansatellites.altervista.org')
soup = BeautifulSoup(response.text, 'html.parser') 
print('fetching PDF links...')
for link in soup('a', href=True):
    if link['href'].endswith('.html') and not link['href'].endswith('Esperimenti.html'):
        response = requests.get(link['href'])
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup('a', href=True):
            if link['href'].endswith('.pdf'):
                pdfs.append(link['href'])

print(f'{len(pdfs)} PDF links found')

if not os.path.exists('pdfs'): os.mkdir('pdfs')

for index, pdf in enumerate(pdfs):
    name = pdf.split('/')[-1]
    with open(f'pdfs/{name}', 'wb') as file:
        response = requests.get(pdf)
        file.write(response.content)
        print(f'downloaded {name} [{index + 1}/{len(pdfs)}]')
import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from aiohttp import ClientError

async def fetch(session, url):
    try:
        async with session.get(url, ssl=False) as response:
            return await response.text(), response.status
    except ClientError as e:
        return str(e), None

async def get_links(session, url):
    html, status = await fetch(session, url)
    if status == 200:
        soup = BeautifulSoup(html, 'html.parser')
        base_url = soup.base['href'] if soup.base else url
        links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]
        return links
    else:
        print(f"Error {status} for {url}")
        return []

async def process_links(links):
    async with aiohttp.ClientSession() as session:
        tasks = [get_links(session, link) for link in links]
        return await asyncio.gather(*tasks)

async def main():
    links = [
        'https://regex101.com/',
        'https://docs.python.org/3/this-url-will-404.html',
        'https://www.nytimes.com/guides/',
        'https://www.mediamatters.org/',
        'https://1.1.1.1/',
        'https://www.politico.com/tipsheets/morning-money',
        'https://www.bloomberg.com/markets/economics',
        'https://www.ietf.org/rfc/rfc2616.txt'
    ]

    result = await process_links(links)

    valid_links = [link for links in result for link in links if link.startswith('http')]

    async with aiofiles.open('links.txt', 'w') as file:
        for link in valid_links:
            await file.write(link + '\n')

asyncio.run(main())

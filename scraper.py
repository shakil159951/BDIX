import os
import requests
from bs4 import BeautifulSoup

TARGET_URL = 'http://198.195.239.50/'
OUTPUT_FILE = 'channels.m3u'


def generate_m3u():
  print('Scraping data from target website...')
  try:
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
            ' like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    }
    response = requests.get(TARGET_URL, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # নিচে আপনার সাইটের এইচটিএমএল স্ট্রাকচার অনুযায়ী ট্যাগ/ক্লাস বসাতে হবে
    # উদাহরণস্বরূপ চ্যানেল আইটেমগুলোর ক্লাস সিলেক্ট করা:
    channels = soup.find_all('div', class_='channel-item')

    if not channels:
      print(
          'Warning: No channels found. Check HTML structure or if site uses'
          ' JSON API.'
      )
      return False

    m3u_content = '#EXTM3U\n'

    for channel in channels:
      name = (
          channel.find('h3').text.strip()
          if channel.find('h3')
          else 'Unknown Channel'
      )
      logo = channel.find('img')['src'] if channel.find('img') else ''
      stream_url = channel.find('a')['href'] if channel.find('a') else ''

      if logo and not logo.startswith('http'):
        logo = TARGET_URL.rstrip('/') + '/' + logo.lstrip('/')

      m3u_content += (
          f'#EXTINF:-1 tvg-logo="{logo}" group-title="Auto Scraped",{name}\n'
      )
      m3u_content += f'{stream_url}\n'

    # পুরোনো ফাইলের সাথে নতুন কন্টেন্টের তুলনা করার জন্য ফাইল সেভ করি
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
      f.write(m3u_content)

    print('M3U playlist generated successfully.')
    return True

  except Exception as e:
    print(f'Error during scraping: {e}')
    return False


if __name__ == '__main__':
  generate_m3u()

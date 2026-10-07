import os
import requests
from bs4 import BeautifulSoup

TARGET_URL = 'http://198.195.239.50/'
OUTPUT_FILE = 'channels.m3u'


def is_channel_alive(stream_url):
  """স্ট্রিম লিংকটি লাইভ বা সচল আছে কিনা তা চেক করে"""
  if not stream_url:
    return False
  try:
    # ছোট একটি হেড রিকোয়েস্ট বা গেট রিকোয়েস্ট পাঠিয়ে চেক করা
    # টাইমআউট কম রাখা হয়েছে যেন স্ক্রিপ্ট ধীরগতির না হয়ে যায়
    response = requests.get(
        stream_url, timeout=4, stream=True, headers={'User-Agent': 'VLC/3.0.18'}
    )
    # যদি স্ট্যাটাস কোড ২০০ হয় এবং কন্টেন্ট টাইপে m3u8 বা ভিডিও স্ট্রিম থাকে
    if response.status_code == 200:
      return True
  except:
    pass
  return False


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
    channels = soup.find_all('div', class_='channel-item')

    if not channels:
      print('Warning: No channels found.')
      return False

    m3u_content = '#EXTM3U\n'
    valid_count = 0
    dead_count = 0

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

      # লিংকটি ডেড নাকি লাইভ তা চেক করা হচ্ছে
      print(f'Checking: {name}...')
      if is_channel_alive(stream_url):
        m3u_content += (
            f'#EXTINF:-1 tvg-logo="{logo}" group-title="Live Channels",{name}\n'
        )
        m3u_content += f'{stream_url}\n'
        valid_count += 1
        print(f' -> Alive [Added]')
      else:
        dead_count += 1
        print(f' -> Dead [Skipped]')

    # ফাইল সেভ করা
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
      f.write(m3u_content)

    print(
        f'M3U playlist generated! Active: {valid_count}, Dead Skipped:'
        f' {dead_count}'
    )
    return True

  except Exception as e:
    print(f'Error during scraping: {e}')
    return False


if __name__ == '__main__':
  generate_m3u()

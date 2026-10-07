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
    response = requests.get(
        stream_url, timeout=4, stream=True, headers={'User-Agent': 'VLC/3.0.18'}
    )
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
      print('Warning: No channels found. Trying generic links extraction...')
      # যদি নির্দিষ্ট ক্লাস না পাওয়া যায়, পেজ থেকে সরাসরি m3u8 লিংক খোঁজার ফলব্যাক
      channels = soup.find_all('a')

    m3u_content = '#EXTM3U\n'
    valid_count = 0
    dead_count = 0

    for channel in channels:
      name = (
          channel.text.strip() if channel.text else 'Unknown Channel'
      )
      stream_url = channel.get('href', '')

      if not stream_url.startswith('http'):
        continue

      logo = ''  # যদি লোগো থাকে লজিক এখানে বসবে

      print(f'Checking: {name}...')
      if is_channel_alive(stream_url):
        m3u_content += (
            f'#EXTINF:-1 tvg-logo="{logo}" group-title="Live Channels",{name}\n'
        )
        m3u_content += f'{stream_url}\n'
        valid_count += 1
        print(' -> Alive [Added]')
      else:
        dead_count += 1
        print(' -> Dead [Skipped]')

    # ফাইল সেভ করা নিশ্চিত করা
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
      f.write(m3u_content)

    print(
        f'M3U playlist generated successfully! Active: {valid_count}, Dead'
        f' Skipped: {dead_count}'
    )
    return True

  except Exception as e:
    print(f'Error during scraping: {e}')
    # ফেইল করলেও যাতে অন্তত বেসিক ফাইল তৈরি থাকে
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
      f.write('#EXTM3U\n')
    return False


if __name__ == '__main__':
  generate_m3u()

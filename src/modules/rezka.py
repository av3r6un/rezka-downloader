from base64 import b64encode, b64decode
from fake_useragent import UserAgent
from src.utils import setup_logger
from itertools import product
from .request import Request
from time import time_ns
import asyncio
import os
import re

logger = setup_logger('StreamsCollector', True)

class Rezka:
  def __init__(self):
    self._request = Request('https://rezka.fi/', True)
    self.headers = {
      'User-Agent': UserAgent().random,
      'Accept': 'application/json, text/javascript, */*; q=0.01',
      'Accept-Encoding': 'gzip, deflate, br, zstd',
      'Cookie': os.getenv('Cookie'),
      'Host': 'rezka.fi',
    }
    
  @staticmethod
  def _clear_trash(data) -> str:
    trashList = ['@', '#', '!', '^', '$']
    trashCodesSet = []
    for i in range(2, 4):
      startchar = ''
      for chars in product(trashList, repeat=i):
        data_bytes = startchar.join(chars).encode('utf-8')
        trash_combo = b64encode(data_bytes)
        trashCodesSet.append(trash_combo)
    arr = data.replace('#h', '').split('//_//')
    trash_string = ''.join(arr)

    for i in trashCodesSet:
      temp = i.decode('utf-8')
      trash_string = trash_string.replace(temp, '')
    
    final_string = b64decode(trash_string+"==")
    return final_string.decode('utf-8')
    
  @staticmethod
  def _parse_subtitle_string(string: str) -> dict:
    pattern = r'\[(.*?)\](https?://\S+)'
    matches = re.match(pattern, string)
    if not matches:
      raise ValueError('Given string does not contain subtitle url')
    return dict(lang=matches.group(1), url=matches.group(2))
  
  @staticmethod
  def _get_best_quality(videos: list[dict]) -> dict:
    quality_order = {"360p": 0, "480p": 1, "720p": 2, "1080p": 3, "1080p Ultra": 4}
    best = max(videos, key=lambda x: quality_order.get(x.get('quality'), -1), default=None)
    if not best: return None
    best_url = best.get('url')
    if best_url.endswith('.mp4'): best['url'] = f'{best_url}:hls:manifest.m3u8'
    return best
  
  def _parse_sources(self, info: list | str):
    video = []
    max_quality_video = None
    if isinstance(info, list):
      return [self._parse_subtitle_string(i) for i in info]
    if isinstance(info, str):
      info = info.split(',')
      for i in info:
        quality = i.split('[')[1].split(']')[0]
        links = re.findall(r'https?://\S+\.(?:m3u8|mp4)', i)
        for v in links: video.append(dict(quality=quality, url=v))
      max_quality_video = self._get_best_quality(video)
      return max_quality_video

  async def _get_stream(self, action, id, translator_id, season=None, episode=None, **kwargs) -> tuple[list, list]:
    data = {'action': action, 'translator_id': translator_id, 'id': id}
    if action == 'get_stream':
      data.update(dict(season=season, episode=episode))
    params = {'t': int(time_ns() / 1000000)}
    info = await self._request.post_page('ajax/get_cdn_series/', self.headers, params, data)
    subtitles = None
    video = None
    if info.get('success'):
      subtitles = info.get('subtitle').split(',') if info.get('subtitle') else None
      video = self._clear_trash(info.get('url'))
    return self._parse_sources(subtitles), self._parse_sources(video)

  async def _make_request(self, action, max_attempts = 3, **kwargs):
    attempt = 0
    delay = 0.5
    while attempt <= max_attempts:
      try:
        return await self._get_stream(action, **kwargs)
      except (UnicodeDecodeError, IndexError):
        attempt += 1
        await asyncio.sleep(delay*attempt)
    else:
      raise ConnectionError('Failed to receive answer from server!')

  async def get_movie(self, **kwargs):
    return await self._make_request('get_movie', **kwargs)
  
  async def get_episode(self, **kwargs):
    return await self._make_request('get_stream', **kwargs)

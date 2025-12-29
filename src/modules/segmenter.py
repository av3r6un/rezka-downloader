from aiohttp import ClientSession, ClientTimeout, TCPConnector, ClientPayloadError, ServerTimeoutError
from urllib.parse import urlparse
from src.utils import setup_logger
from src.utils import Progress
from m3u8 import M3U8
import asyncio
import shutil
import time
import sys
import os
import re

logger = setup_logger('Segmenter', True)

class Segmenter:
  DR_ATTEMPTS = 5
  MAX_ELEMENTS = 70
  timeout = 6 * MAX_ELEMENTS
  segments_time: float
  
  def __init__(self, root_folder, outside_ide=False) -> None:
    self.ROOT_FOLDER = root_folder
    self.outside_ide = outside_ide
    self.session = None
    self.progress = None
    self.cache = os.path.abspath(os.path.join(self.ROOT_FOLDER, 'cache', 'files'))
  
  @staticmethod
  def _extract_endpoint(url):
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}/{"/".join(parsed_url.path.split("/")[:-1])}/'
  
  @staticmethod
  def normal_time(seconds):
    h, r = divmod(int(seconds), 3600)
    m, s = divmod(r, 60)
    return f'{h:02d}:{m:02d}:{s:02d}'
  
  def __init_session(self):
    self.loop = asyncio.get_event_loop()
    connector = TCPConnector(limit=self.MAX_ELEMENTS)
    timeout = ClientTimeout(total=self.timeout, sock_read=10)
    self.session = ClientSession(connector=connector, trust_env=True, timeout=timeout)
  
  async def __close(self):
    await self.session.close()
  
  async def _extract_fragments(self):
    async with self.session.get(self.source) as resp: # add source
      info = await resp.read()
    self.manifest = M3U8(info.decode('utf-8'))
    self.segments = [link.replace('/', '') for link in info.decode('utf-8').split('\n') if link.endswith('.ts')]
    self._length = len(self.segments)
    self.progress.start(self._length)
  
  async def _download_segment(self, segment):
    fp = os.path.join(self.cache, f'{self.filename}')
    if not os.path.exists(fp): os.makedirs(fp, exist_ok=True)
    seg_num = re.findall(r'-\d+-', segment)[0].replace('-', '')
    filename = f'{fp}/{self.filename}_{seg_num}.ts'
    segment = segment[1:]
    return await self._fetch_segment(segment, filename, seg_num)
  
  async def _fetch_segment(self, segment, filename, seg_num):
    attempt = 0
    while attempt <= self.DR_ATTEMPTS:
      try:
        async with self.session.get(f'{self.endpoint}{segment}') as resp:
          content = await resp.read()
        with open(filename, 'wb') as file:
          file.write(content)
        self.progress.increase()
        return filename
      except (ClientPayloadError, ServerTimeoutError):
        attempt += 1
        if attempt:
          logger.error(f'Some troubles downloading seg{seg_num}. Retrying x{attempt}')
    else:
      raise IndexError(seg_num)
  
  async def _download_segments(self):
    try:
      logger.info(f'Starting downloading segments for {self.filename}')
      tasks = [asyncio.create_task(self._download_segment(segment)) for segment in self.segments]
      self.dd_started = time.time()
      self.segments_list = await asyncio.gather(*tasks)
      self.segments_time = round(time.time() - self.st, 1)
      logger.info(f'Downloaded all segments in {round(self.segments_time, 1)}s')
      
      return True
    except TimeoutError:
      print()
      logger.error(f'Not enough time ({self.timeout}) to download all fragments.')
      sys.exit(-1)

  def _create_alt_manifest(self):
    for segment in self.manifest.segments:
      seg_num = re.findall(r'-\d+-', segment.uri)[0].replace('-', '')
      segment.uri = f'{self.filename}/{self.filename}_{seg_num}.ts'
    return self._dump_manifest()
  
  def _dump_manifest(self):
    fp = os.path.join(self.cache, f'{self.filename}_manifest.m3u8')
    with open(fp, 'w') as f:
      f.write(self.manifest.dumps())
    return fp
  
  def _check_integrity(self):
    fp = os.path.join(self.cache, f'{self.filename}')
    segments = [file for file in os.listdir(fp) if file.endswith('.ts')]
    if len(segments) == self._length:
      return True
    else:
      logger.error(f'Downlaoded segments length mismatch manifest.')
      sys.exit(-1)
      
  async def __call__(self, filename, video) -> tuple[str, float]:
    self.st = time.time()
    self.filename = filename
    self.source = video
    self.__init_session()
    self.endpoint = self._extract_endpoint(video)
    self.progress = Progress(filename, self.outside_ide)
    await self._extract_fragments()
    await self._download_segments()
    await self.__close()
    self._check_integrity()
    return self._create_alt_manifest(), self.segments_time
  
  def clear_cache(self):
    for entry in os.listdir(self.cache):
        full_path = os.path.join(self.cache, entry)
        if os.path.isfile(full_path) or os.path.islink(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)

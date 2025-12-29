from aiohttp import ClientSession, ClientTimeout, ClientError
from src.utils import setup_logger
from asyncio import TimeoutError
import json
import os


logger = setup_logger('Request', True)

class Request:  
  _base_uri: str = None
  
  def __init__(self, base_uri, debug=False):
    self._base_uri = base_uri
    self._debug = debug
    self.session = None
    
  async def _init_session(self):
    self.session = ClientSession(
      base_url = self._base_uri,
      timeout=ClientTimeout(total=20.0),
      raise_for_status=False
    )
  
  async def __send(self, method, url, headers=None, params=None, data=None, response='json') -> dict | str:
    await self._init_session()
    data, json = (data, None) if 'form' in headers.get('Content-Type') else (None, data)
    try:
      async with self.session.request(method, url, headers=headers, params=params, json=json, data=data) as resp:
        if self._debug: logger.info(f'{resp.status} {resp.reason} | [{resp.method}] {resp.url}')
        return await getattr(resp, response)()
    except (ClientError, TimeoutError) as err:
      logger.error(str(err))
      if self._debug: logger.info(str(await resp.text()))
      return None
    except ArithmeticError:
      logger.error((await resp.text()))
    finally:
      await self.__close()
      
  async def get(self, url, headers=None, params=None) -> dict:
    return await self.__send('GET', url, headers, params)
  
  async def get_page(self, url, headers=None, params=None) -> str:
    return await self.__send('GET', url, headers, params, response='text')
  
  async def post(self, url, headers: dict = {}, params=None, json=None) -> dict:
    return await self.__send('POST', url, headers, params, json)
  
  async def post_page(self, url, headers: dict = {}, params=None, data=None) -> str | dict:
    headers.update({'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
    resp = await self.__send('POST', url, headers=headers, params=params, data=data, response='text')
    try:
      return json.loads(resp)
    except json.JSONDecodeError:
      return resp
      
  async def __close(self):
    await self.session.close()

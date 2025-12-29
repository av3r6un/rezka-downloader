from src.wrappers import Episodes, SeriesSeasons
from .request import Request
import os


class Metadata:
  def __init__(self) -> None:
    self._request = Request('https://kinopoiskapiunofficial.tech/')
    self.headers = {
      'X-API-KEY': os.getenv('KP_KEY'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
    self.response = None

  async def _get_seasons(self, id, items: SeriesSeasons) -> list:
    url = 'api/v2.2/films/{id}/seasons'.format(id=id)
    response = await self._request.get(url, self.headers)
    gathered_episodes = []
    
    for item in response['items']:
      for episode in item['episodes']:
        if items[item['number']] and episode['episodeNumber'] in items[item['number']]:
          gathered_episodes.append(episode)
    
    return gathered_episodes
  
  async def _get_name(self, id) -> str:
    url = 'api/v2.2/films/{id}'
    self.response = await self._request.get(url, self.headers)
    return self.response.get('nameRu') or self.response.get('nameEn') or self.response.get('nameOriginal')
  
  async def get_episodes(self, id, episode_items) -> Episodes:
    title = await self._get_name(id)
    return Episodes(title, await self._get_seasons(id, episode_items))
  
  async def get_info(self, id) -> tuple[str, str, int]:
    name = await self._get_name(id)
    return name, self.response.get('year') or self.response.get('startYear')
    

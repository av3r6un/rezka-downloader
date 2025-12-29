from typing import List


class Source:
  url: str
  lang: str = None
  
  def __init__(self, url, lang=None):
    self.url = url
    self.lang = lang
    
  @property
  def json(self):
    return dict(url=self.url, lang=self.lang)


class Episode:
  title: str
  index: int
  season: int
  video_source: Source = None
  subtitle_source: Source = None
  filename: str = None
  _metatitle: str = None
  
  def __init__(self, seasonNumber, episodeNumber, nameRu, nameEn, title, **kwargs) -> None:
    self.season = seasonNumber
    self._metatitle = title
    self.index = episodeNumber
    self.title = nameRu or nameEn
    
  def add_source(self, type, url, lang=None, **kwargs):
    setattr(self, f'{type}_source', Source(url, lang))
      
  def set_filename(self, filename) -> None:
    self.filename = f'{filename}_{self.idx}'
    
  @property
  def idx(self):
    return f'S{str(self.season).zfill(2)}E{str(self.index).zfill(2)}'
  
  @property
  def streams(self):
    return dict(season=self.season, episode=self.index)

  @property
  def json(self):
    return dict(filename=self.filename, metatitle=self.metatitle, video=self.video_source.url, subtitles=self.subtitle_source.url) 
  
  @property
  def meta(self):
    main = {'-metadata': f'title={self.metatitle}', '-metadata:s:a:0': f'language={self.video_source.lang}'}
    if self.subtitle_source.url:
      main.update({'-metadata:s:s:0': f'language={self.subtitle_source.lang}'})
    return main

  @property
  def metatitle(self):
    return f'{self._metatitle} {self.season} сезон {self.index} серия - {self.title}'

class Episodes(List[Episode]):
  def __init__(self, title, episodes, **kwargs):
    for episode in episodes:
      self.append(Episode(title=title, **episode))
  
  def first(self) -> Episode:
    return self[0]
  
  @property
  def json(self):
    return [dict(title=e.title, filename=f'{self._filename}_{e.idx}') for e in self]

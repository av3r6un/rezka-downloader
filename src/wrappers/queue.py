from src.utils import parse_items, FileLoader
from typing import List


class SeriesSeason:
  season: int
  episodes: list[int]
  
  def __init__(self, season, episodes, **kwargs):
    self.season = season
    self.episodes = parse_items(episodes)

  @property
  def json(self):
    return dict(season=self.season, episodes=self.episodes)

class SeriesSeasons(List[SeriesSeason]):
  def __init__(self, *args):
    for arg in args:
      self.append(SeriesSeason(**arg))

  def __getitem__(self, season) -> list[int]:
    for item in self:
      if item.season == season:
        return item.episodes

  @property
  def json(self):
    return [a.json for a in self]


class QueueItem:
  media_type: str
  kp_id: int
  hdr_id: int
  translator_id: int
  title: str
  video_lang: str
  series: SeriesSeasons = None
  year: int = None
  subtitles_lang: str = None
  video_encoder: str = None
  audio_encoder: str = None
  
  def __init__(self, media_type, kp_id, hdr_id, translator_id, series, title, video_lang, subtitles_lang=None, video_encoder='copy', audio_encoder='copy', format='mp4', **kwargs) -> None:
    self.media_type = media_type
    self.kp_id = kp_id
    self.hdr_id = hdr_id
    self.translator_id = translator_id
    self.title = title
    self.video_lang = video_lang
    self.subtitles_lang = subtitles_lang
    self.series = SeriesSeasons(*series) if media_type == 'tv' else None
    self.video_encoder = video_encoder
    self.audio_encoder = audio_encoder
    self.format = format
    
  @property
  def meta(self):
    return dict(id=self.kp_id, episode_items=self.series)
  
  @property
  def streams(self):
    return dict(id=self.hdr_id, translator_id=self.translator_id)
  
  @property
  def metainfo(self):
    return dict(media_type=self.media_type, vcodec=self.video_encoder, acodec=self.audio_encoder, format=self.format, subtitles_lang=self.subtitles_lang, video_lang=self.subtitles_lang)
    
  @property
  def json(self):
    return dict(media_type=self.media_type, kp_id=self.kp_id, hdr_id=self.hdr_id, translator=self.translator_id, title=self.title, sub_lang=self.subtitles_lang, video_lang=self.video_lang, series=self.series.json if self.series else None, year=self.year)


class Queue(List[QueueItem], FileLoader):
  def __init__(self, filename) -> None:
    queue = self.load_file(filename)
    self._make_init(queue)
    
  def _make_init(self, queue: dict):
    for media_type, items in queue.items():
      for item in items:
        self.append(QueueItem(media_type, **item))

  @property
  def json(self):
    return [a.json for a in self]

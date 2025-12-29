from .wrappers import Queue
from .config import Settings
from .modules import Metadata, Rezka, Segmenter, Converter
from .utils import setup_logger
import os

settings = Settings()
metadata = Metadata()
rezka = Rezka()
segments = Segmenter(settings.ROOT)
conv = Converter(settings.ROOT)

logger = setup_logger('Main', True)

# Make better progress visualization
# Make annotation to each function
# deploy on gh

async def main():
  q = Queue(settings.MANIFEST)
  for item in q:
    if item.media_type == 'tv':
      items_meta = await metadata.get_episodes(**item.meta)
      for episode in items_meta:
        episode.set_filename(item.title)
        while True:
          ss, vs = await rezka.get_episode(**item.streams, **episode.streams)
          if vs.get('quality') in ['1080p', '1080p Ultra']:
            break
          print('Current quality is:', vs.get('quality'))
          choice = input('Do u want to continue?').strip().lower()
          if choice == 'y':
            break
        ss = next(s for s in ss if item.subtitles_lang in s['lang'].lower())
        episode.add_source('subtitle', **ss)
        episode.add_source('video', lang=item.video_lang, **vs)
        manifest, seg_time = await segments(episode.filename, episode.video_source.url)
        state, conv_time = conv(manifest_path=manifest, **item.metainfo, **episode.json)
        if state:
          logger.info(f'File {episode.filename} successfully downloaded in {segments.normal_time(seg_time + conv_time)}.')
          segments.clear_cache()
          logger.info(f'Intermediate cache cleared!')
        else:
          logger.error(f'There are some errors while downloading. Please, check logs file for more info.')
    else:
      title, year = await metadata.get_info(item.kp_id)
      while True:
        ss, vs = await rezka.get_movie(**item.streams)
        if vs.get('quality') in ['1080p', '1080p Ultra']:
          break
        print('Current quality is:', vs.get('quality'))
        choice = input('Do u want to continue?').strip().lower()
        if choice == 'y':
          break
        ss = next(s for s in ss if item.subtitles_lang in s['lang'].lower())
        manifest, seg_time = await segments(f'{item.title}_({year})', vs.get('url'))
        state, conv_time = conv(
          filename=f'{item.title}_({year})', manifest_path=manifest, subtitles=ss.get('url'), **item.metainfo,
          metatitle=f'{title} ({year})'
        )

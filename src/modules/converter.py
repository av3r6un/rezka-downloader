from src.utils import setup_logger
import ffmpeg
import time
import sys
import os

logger = setup_logger('Converter', True)

class Converter:
  filename: str = None
  output_filename: str = None
  time_consumed: float = 0.0
  
  langs = {
    'eng': 'English', 'rus': 'Русский'
  }
  
  def __init__(self, root_folder, loglevel='error') -> None:
    self.ROOT_FOLDER = root_folder
    self.loglevel = loglevel
    
  def _collect_params(self, **kwargs):
    params = {
      'c:v': kwargs.get('vcodec', 'copy'), 'c:a': kwargs.get('acodec', 'copy'),
      'format': kwargs.get('format', 'mp4'), 'metadata:s:a:0': f"language={kwargs.get('video_lang', 'eng')}",
      'strict': -2, 'metadata': f"title={kwargs.get('metatitle')}"
    }
    args = ['-loglevel', self.loglevel, '-metadata:s:a:0', f'title={self.langs[kwargs.get("video_lang", "eng")]}']
    if self.subtitles:
      params.update({'metadata:s:s:0': f"language={kwargs.get('subtitles_lang', 'eng')}", 'c:s': 'mov_text'})
      args.insert(2, '-i')
      args.insert(3, self.subtitles)
      args.extend(('-metadata:s:s:0', f'title={self.langs[kwargs.get("subtitles_lang", "eng")]}'))
    return args, params
  
  def _concat(self, manifest_path, **kwargs):
    args, params = self._collect_params(**kwargs)
    output_path = os.path.join(self.ROOT_FOLDER, 'downloads', self.output_filename)
    output_folder, _ = os.path.split(output_path)
    if not os.path.exists(output_folder): os.makedirs(output_folder, exist_ok=True)
    try:
      logger.info(f'Conversion started for {self.filename}.')
      process = (
        ffmpeg
        .input(manifest_path)
        .output(output_path, **params)
        .global_args(*args)
        .overwrite_output()
        .run_async(pipe_stdout=True)
      )
      process.wait()
      return True
    except Exception as ex:
      logger.error(f'Conversion failed for {self.filename}. Traceback: {str(ex)}')
  
  def _check_download(self):
    fp = os.path.join(self.ROOT_FOLDER, 'downloads', self.output_filename)
    if not os.path.exists(fp):
      logger.error(f'File {self.filename} not found in download folder. Download failed!')
      sys.exit(-1)
    return True
  
  def _finish_conversion(self):
    self._check_download()
    self.time_consumed = round(time.time() - self.st)
    logger.info(f'Conversion for {self.filename} successfully ended. Consumed: {self.time_consumed}s')
    
  def __call__(self, media_type: str, filename: str, manifest_path, subtitles=None, **kwargs):
    self.filename = filename
    self.output_filename = os.path.join(media_type, f'{filename}.{kwargs.get("format", "mp4")}')
    self.subtitles = subtitles
    self.st = time.time()
    try:
      state = self._concat(manifest_path, **kwargs)
      if state: self._finish_conversion()
    except Exception as ex:
      logger.error(f'An error occured while converting. {str(ex)}')
      state = False
    return state, self.time_consumed

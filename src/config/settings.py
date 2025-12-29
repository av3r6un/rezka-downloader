from src.utils import FileLoader
from dotenv import load_dotenv
import os

class Settings(FileLoader):
  ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
  
  def __init__(self) -> None:
    load_dotenv(os.path.join(self.ROOT, 'config', '.env'))
    self.LOG_FILE = os.path.join(self.ROOT, 'logs', 'app.log')
    self.MANIFEST = os.path.abspath(os.path.join(self.ROOT, '..', 'manifest.yaml'))
    self.MAX_RETRIES = 3
    os.makedirs(os.path.split(self.LOG_FILE)[0], exist_ok=True)
    self.DEBUG = bool(int(os.getenv('DEBUG', '0')))

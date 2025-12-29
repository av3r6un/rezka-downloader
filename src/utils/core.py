from yaml import safe_load
import sys


class FileLoader:
  def __init__(self, filename = None, **kwargs) -> None:
    self.filename = filename

  def load_file(self, path) -> dict:
    try:
      with open(path, 'r', encoding='utf-8') as f:
        return safe_load(f)
    except FileNotFoundError:
      print(f'{path} file not found!')
      sys.exit(-1)


def parse_items(items_string: str) -> list[int]:
  result = []
  for part in items_string.split(','):
    part = part.strip()
    if '-' in part:
      start, end = map(int, part.split('-', 1))
      result.extend(range(start, end + 1))
    else:
      result.append(int(part))
  return result

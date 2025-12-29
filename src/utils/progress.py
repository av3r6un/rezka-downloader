from colorama import Fore

class Progress:
  outside_ide = False
  def __init__(self, filename, outside_ide=False) -> None:
    self.downloaded = 0
    self.filename = filename
    self.outside_ide = outside_ide

  def start(self, sl):
    self.sl = sl

  def increase(self):
    formating = ['00d', '01d', '02d', '03d', '04d', '05d']
    fmt = formating[len(str(self.sl))]
    self.downloaded += 1
    percent = int(round(self.downloaded / self.sl * 100))
    if self.outside_ide:
      print(self.filename, percent, f'{self.downloaded:{fmt}}/{self.sl:{fmt}}')
    else:
      left = 0 + percent
      right = 100 - percent
      print(self.filename, ':', end='\r')
      print(f'{self.filename}: ', Fore.CYAN, '\u25A0' * left, ' ' * right, Fore.RESET, f'{self.downloaded:{fmt}}/{self.sl:{fmt}}', end='\r')
      if self.downloaded == self.sl:
        print()

import string
import random
from io import BytesIO
from itertools import count
from typing import Union, List, Optional
from pathlib import Path
from os import PathLike
from os.path import getsize
from PIL import Image

class _JustMakeItToSize(Image.ImageTransformHandler):
	@staticmethod
	def transform(size, image, resample, fill):
		sol = Image.new(image.mode, size, color = fill)
		sol.paste(image)
		return sol

JustMakeItToSize = _JustMakeItToSize()

PathType = Union[str, bytes, PathLike]

class ImageProcess:
	_path: Path
	_filename: List[Path]
	def __init__(self, path: PathType = ''):
		self._path = Path(path)
		self._filename = []
	@property
	def path(self):
		return self._path
	@path.setter
	def path(self, p: PathType):
		self._path = Path(p)
	@property
	def filename(self):
		return self._filename
	def add_file(self, file: PathType):
		self._filename.append(Path(file))
	@staticmethod
	def merge_image(i1: Image, i2: Image, fillcolor = 0, vertical = True) -> Image:
		w1, h1 = i1.size
		w2, h2 = i2.size
		if vertical:
			sol = i1.transform((max(w1, w2), h1 + h2), JustMakeItToSize, fill = fillcolor)
			sol.paste(i2, (0, h1))
		else:
			sol = i1.transform((w1 + w2, max(h1, h2)), JustMakeItToSize, fill = fillcolor)
			sol.paste(i2, (w1, 0))
		return sol
	def annex_start(self, max_size: int = 20 * 1000 * 1000, save_dir: Optional[PathType] = None, *, remain_mode: bool = False, fillcolor = 0, vertical = True):
		#remain_mode = False to use google cloud vision

		if save_dir is None:
			save_dir = self._path
			#if _path doesn't exist, an error will be risen below.
		else:
			save_dir = Path(save_dir)
			if not save_dir.exists():
				save_dir.mkdir(parents = True)

		full_name = [self._path / n for n in self._filename]
		full_name = [n for n in full_name if n.is_file()]
		#with Py 3.8
		#full_name = [(fullpath := self._path / n) for n in self._filename if fullpath.is_file()]

		work_code_length = 16
		work_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k = work_code_length))
		
		savename_template = '{work_code}_{now_count}.png'

		ite = self.annex(full_name, work_code, savename_template, max_size, save_dir, remain_mode, fillcolor, vertical)

		return (savename_template, work_code, ite)
	@classmethod
	def annex(cls, full_name: List[PathType], work_code: str, savename_template: str, max_size: int, save_dir: PathType, remain_mode: bool, fillcolor, vertical, max_pixel = 4096):
		counter = count()
		now_count = next(counter)

		too_large = lambda img: (vertical and img.height > max_pixel) or (not vertical and img.width > max_pixel)

		img = None
		rem = 0
		for p in full_name:
			now_i = Image.open(p)
			if img is None:
				img_tmp = now_i
			else:
				img_tmp = cls.merge_image(img, now_i, fillcolor = fillcolor, vertical = vertical)
			fpath = save_dir / savename_template.format(work_code = work_code, now_count = now_count)
			with BytesIO() as byte:
				#img_tmp.save(fpath)
				img_tmp.save(byte, format = 'png')
				size = byte.tell()
				if not remain_mode:
					if size > max_size or too_large(img_tmp):
						img.save(fpath)
						if img is not None:
							img = now_i
						now_count = next(counter)
					else:
						img = img_tmp
				else:
					rem_tmp = size % max_size
					if rem_tmp <= rem or too_large(img_tmp):
						if img is not None:
							img.save(fpath)
							img = now_i
							#rem = (rem_tmp - rem) % max_size #!!!just approaching!!!
							now_count = next(counter)
							#fpath = save_dir / savename_template.format(work_code = work_code, now_count = now_count)
							#img.save(fpath)
							img.save(byte, format = 'png')
							rem = (byte.tell() - rem) % max_size
						else:
							#img is None, rem is 0, it is no matter
							#and that means img won't be None again.
							img = img_tmp
					else:
						img = img_tmp
						rem = rem_tmp
				yield
		if img is not None:
			img.save(save_dir / savename_template.format(work_code = work_code, now_count = now_count))
		return next(counter)

if __name__ == '__main__':
	#back = Image.new('RGBA', (100, 100))
	#im = Image.open('test.png')
	#sol = ImageProcess.merge_image(back, im)
	#sol.show()
	#back.paste(im, (100, 100))
	#back.show()
	process = ImageProcess(path = '新增資料夾')
	#for file in Path('新增資料夾').glob('*.png'):
	#	process.add_file(file.parts[-1])
	#	print(file.parts[-1])
	process.add_file('15FuyueventE1.png')
	process.add_file('18fuyueventE1.png')
	_, _, ite = process.annex_start()
	try:
		while True:
			next(ite)
	except StopIteration as e:
		print(e.value)
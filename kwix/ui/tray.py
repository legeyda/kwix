import PIL.Image
import pystray
import pkg_resources
import threading
from typing import Callable

class TrayIcon():
	def __init__(self):
		self.on_show: Callable[[], None] = lambda: None
		self.on_quit: Callable[[], None] = lambda: None
	def run(self, callback: Callable[[], None]):
		image = PIL.Image.open(pkg_resources.resource_filename('kwix', 'logo.jpg'))
		menu = pystray.Menu(
			pystray.MenuItem('kwix', self.on_show, default=True),
			pystray.MenuItem('exit', self.on_quit))
		self._icon = pystray.Icon('kwix', image, 'Kwix', menu, visible = True)
		if 'darwin' in pystray.Icon.__module__:
			self._icon.run_detached(None)
		else:
			threading.Thread(target=self._icon.run).start()
		callback()

	def stop(self):
		self._icon.stop()

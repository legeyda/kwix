import PIL.Image
import pystray
import pkg_resources
import threading

class TrayIcon():
	def __init__(self):
		self.on_show = lambda *args: ...
		self.on_quit = lambda *args: ...
	def run(self, callback):
		image = PIL.Image.open(pkg_resources.resource_filename('kwix', 'logo.jpg'))
		menu = pystray.Menu(
			pystray.MenuItem('kwix', self.on_show, default=True),
			pystray.MenuItem('exit', self.on_quit))
		self._icon = pystray.Icon('kwix', image, 'Kwix', menu, visible = True)
		if 'darwin' in pystray.Icon.__module__:
			self._icon.run_detached()
		else:
			threading.Thread(target=self._icon.run).start()
		callback()

	def stop(self):
		self._icon.stop()





import kwix.logic
from kwix.logic import Logic
from kwix.plugin import Machinist
from kwix.ui.tk import KwixWindow
import kwix.ui.tray
import pynput
import kwix.ui.tray
import kwix.server
import keyboard


# class KwixApp:
# 	def __init__(self, window, actions):
# 		pass
# 	def run(self):
# 		self._window = KwixWindow()
# 		self._window.show()

# 		#self._icon = TrayIcon()
# 		#self._icon.on_show = self._window.show
# 		#self._icon.on_quit = self.quit
# 		#self._icon.run()
# 	def window_hide(self):
# 		pass
# 	def quit(self):
# 		self._window.quit()
# 		self._icon.stop()


def x():
	from pynput import keyboard

	def on_activate():
		print('Global hotkey activated!')

	def for_canonical(f):
		return lambda k: f(l.canonical(k))

	hotkey = keyboard.HotKey(
		keyboard.HotKey.parse('<f2>'),
		on_activate)
	with keyboard.Listener(
			on_press=for_canonical(hotkey.press),
			on_release=for_canonical(hotkey.release)) as l:
		l.join()

# class HotKeyListener:
# 	def __init__()


def y():

	def on_press(*args):
		print('press', *args)

	pynput.keyboard.Listener(on_press=on_press, on_release=lambda *args: print('release', *args)).start()
	#	listener.join()


	# hotkey = pynput.keyboard.HotKey(pynput.keyboard.HotKey.parse('<f2>'), lambda *args: print('f2 pressed!'))

	
	#pynput.keyboard.GlobalHotKeys({ '<ctrl>+<f1>': lambda *args: print('y---pressed') }).start()
	

class KwixApp():
	def run(self):
		self._tray = kwix.ui.tray.TrayIcon()
		self._tray.on_show = self._window_toggle
		self._tray.on_quit = self._quit
		self._reg_hotkeys()
		self._tray.run(self._run_ui)

	def _reg_hotkeys(self):
		pynput.keyboard.GlobalHotKeys({'<ctrl>+;': self._window_toggle}).start()

	def _run_ui(self):
		logic = Logic([
			Machinist('123', 'one two three', 'description of one two three'),
			Machinist('321'),
		])
		self._window = KwixWindow(logic)
		kwix.server.run_server(self._window)
		self._window.run()

	def _run_server(self, context: kwix.logic.Context):

		kwix.server.run_server(context)

	def _window_toggle(self):
		if not self._window.is_visible():
			self._window.show()
		else:
			self._window.hide()

	def _quit(self):
		self._window.quit()
		self._tray.stop()

def main():
	KwixApp().run()

import http.server
import http.client
import threading

import kwix.logic


PORT=23844

def show_remote_widow(host, port):
	host = "127.0.0.1:" + PORT
	conn = http.client.HTTPSConnection(host)
	conn.request("GET", "/show-window")
	response = conn.getresponse()
	if response.status != 200:
		pass
		

def run_server(window: kwix.logic.Window):
	class Handler(http.server.BaseHTTPRequestHandler):
		def do_POST(self):
			if self.path == '/show-window':
				window.show()
				self.back(200, 'ok')
			elif self.path == '/hide-window':
				window.hide()
				self.back(200, 'ok')
			else:
				self.back(400, 'wrong request')
		def back(self, status: int, msg: str):
			self.send_response(status)
			self.send_header("Content-Type", "application/json")
			self.end_headers()
			self.wfile.write(b'{"msg":"' + bytes(msg, 'UTF-8') + b'"}')

	httpd = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
	threading.Thread(target = httpd.serve_forever).start()
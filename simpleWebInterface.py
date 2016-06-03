#!/usr/bin/python3
# -*- coding: utf-8 -*

from http.server import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep, remove
import cgi
from datetime import datetime
from re import sub

HTML_FILE_NAME = '.form.html'
PORT_NUMBER = 8080

def createHTML(title, form, button_name):
	html = """<!DOCTYPE html>
<html>
	<head>
		<title>%s</title>
		<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css' integrity='sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7' crossorigin='anonymous'>
		<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css' integrity='sha384-fLW2N01lMqjakBkx3l/M9EahuwpSfeNvV63J5ezn3uZzapT0u7EYsXMjQV+0En5r' crossorigin='anonymous'>
		<style> html{background-color:white} body{width:800px; margin:auto; padding:10px; background-color:aliceblue} h1{margin-left:10px;} h3{margin-left:30px;} </style>
	</head>
	<body>
		<h1>%s</h1>
		<form method="POST" action="/" class="form-horizontal">""" % (title, title)

	for fieldset in form:
		html += """
			<fieldset>
				<legend>%s:</legend>""" % fieldset['legend']
		for field in fieldset['inputs']:
			name = field['name']
			label = name.title() if 'label' not in field else field['label']
			type = 'text' if 'type' not in field else field['type']

			tooltip = '' if 'tooltip' not in field else 'title="%s"' % field['tooltip']
			placeholder = '' if 'placeholder' not in field else 'placeholder="%s"' % field['placeholder']
			required = '' if 'required' not in field or field['required'] == False else 'required'

			html += """
				<div class="form-group">
					<label for="%s" class="col-sm-2 control-label">%s</label>
					<div class="col-sm-10">
						""" % (name, label)
			html += ('<textarea %s></textarea>' if type == 'textarea' else '<input type="' + type + '" %s/>') \
				% ('class="form-control" id="%s" name="%s" %s %s %s' \
					% (name, name, placeholder, tooltip, required))
			html += """
					</div>
				</div>"""

		html += """
			</fieldset>"""

	html += """
			<div class="form-group">
				<div class="col-sm-offset-2 col-sm-10">
					<button type="submit" class="btn btn-default">%s</button>
	    		</div>
			</div>
		</form>
	</body>
</html>""" % button_name

	with open(HTML_FILE_NAME, 'w') as f:
		f.write(html)

# This class will handles any incoming request from the browser
class RequestHandler(BaseHTTPRequestHandler):

	# Handler for the GET requests
	def do_GET(self):
		self.path = HTML_FILE_NAME if self.path == '/' else ''
		try:
			if self.path.endswith('.html'):
				with open(curdir + sep + self.path, 'r') as f:
				    self.send_response(200)
				    self.send_header('Content-type', 'text/html')
				    self.end_headers()
				    self.wfile.write(bytes(f.read(), 'UTF-8'))
			return

		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)

	# Handler for the POST requests
	def do_POST(self):
		if self.path == '/':
			form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=
				{'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type']})
			self.send_response(200)
			self.end_headers()
			self.wfile.write(bytes(self.process(form), 'UTF-8'))
			return

def serve(title, form, button_name, callback):
	try:
		# Create a web server and define the handler to manage the incoming request
		createHTML(title, form, button_name)
		host = ('', PORT_NUMBER)

		handlerCls = RequestHandler
		handlerCls.process = callback

		server = HTTPServer(host, handlerCls)
		print('Started httpserver on port %i.' % PORT_NUMBER)

		#Wait forever for incoming htto requests
		server.serve_forever()

	except KeyboardInterrupt:
		print('Interrupted by the user - shutting down the web server.')
		server.socket.close()
		remove(HTML_FILE_NAME)

#!/usr/bin/python3
# -*- coding: utf-8 -*

from http.server import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep, remove
import cgi
from datetime import datetime
from re import sub
from os.path import abspath, isfile
from re import sub

# This class will handles any incoming request from the browser
class _RequestHandler(BaseHTTPRequestHandler):

	# Handler for the GET requests
	def do_GET(self):
		if self.path == '/':
			self.send_response(200)
			self.send_header('Content-type', 'text/html; charset=utf-8')
			self.end_headers()
			self.wfile.write(bytes(self.html, 'UTF-8'))
		return

	# Handler for the POST requests
	def do_POST(self):
		if self.path in ['/', '/update']:
			form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=
				{'REQUEST_METHOD':'POST', 'CONTENT_TYPE':'text/plain'})
			self.send_response(200)
			self.end_headers()
			if self.path == '/':
				self.wfile.write(self.on_valid(form))
			elif self.path == '/update':
				self.on_update(form)
			return

class _Input:
	def __init__(self, id, name, type, value, hint, placeholder, required, pattern, unit):
		self.id          = id
		self.name        = name
		self.type        = type
		self.value       = value
		self.hint        = hint
		self.placeholder = placeholder
		self.required    = required
		self.pattern     = pattern
		self.unit        = unit

class Fieldset:
	def __init__(self, legend):
		self.legend = legend
		self.inputs = {}

	def add(self, name, type='text', value='', hint=None, placeholder=None, required=False, pattern=None, unit=None):
		id = sub('[^_a-z0-9.]+', '', name.replace(' ', '_').lower())
		self.inputs[id] = _Input(id, name, type, value, hint, placeholder, required, pattern, unit)

class Form:
	def __init__(self, fieldsets, ref_on_update, ref_on_valid, title='A simple form', button_name='Send', config_filepath='dachs.conf', port_number=8080):
		self.form = fieldsets
		self.parameters = {}
		self.ref_on_update = ref_on_update
		self.ref_on_valid = ref_on_valid
		self.title = title
		self.button_name = button_name
		self.config_filepath = abspath(config_filepath)
		self.port_number = port_number

		self._init_config_file()
		self._serve()

	def on_update(self, form):
		self.parameters[form['key'].value] = form['value'].value
		with open(self.config_filepath, 'w') as f:
			f.writelines(['%s=%s\n' % (e[0], e[1]) for e in self.parameters.items()])
		self.ref_on_update(form['key'].value, form['value'].value)

	def on_valid(self, form):
		info = self.ref_on_valid(self.parameters)
		return bytes(self._create_form() if info is None else self._create_info(info), 'UTF-8')

	def _serve(self):
		try:
			handlerCls = _RequestHandler
			handlerCls.on_update = self.on_update
			handlerCls.on_valid = self.on_valid
			handlerCls.html = self._create_header() + self._create_form() + self._create_footer()
			server = HTTPServer(('', self.port_number), handlerCls)
			print('Web server started. Please go to 127.0.0.1:%i and fill the form.' % self.port_number)
			server.serve_forever()
		except KeyboardInterrupt:
			print('Interrupted by the user - shutting down the web server.')
			server.socket.close()

	def _init_config_file(self):
		if isfile(self.config_filepath):
			with open(self.config_filepath, 'r') as f:
				fieldset_id = ''
				for line in f:
					if line[0] != '#':
						keyval = [s.strip() for s in line.split('=', 1)]
						self.parameters[keyval[0]] = keyval[1]
		else:
			with open(abspath(self.config_filepath), 'w+') as f:
				for fieldset in self.form:
					f.write('## %s ##\n' % fieldset.legend)
					for input_id, input in fieldset.inputs.items():
						f.write('%s=%s\n' % (input.id, input.value))
						self.parameters[input.id] = input.value

	def _create_header(self):
		return """<!DOCTYPE html>
	<html>
		<head>
			<title>%s</title>
			<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
			<meta content="utf-8" http-equiv="encoding">
			<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css' integrity='sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7' crossorigin='anonymous'>
			<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css' integrity='sha384-fLW2N01lMqjakBkx3l/M9EahuwpSfeNvV63J5ezn3uZzapT0u7EYsXMjQV+0En5r' crossorigin='anonymous'>
			<style> html{background-color:white} body{width:800px; margin:auto; padding:10px; background-color:aliceblue;} form{margin-right: 15px;}</style>
		</head>
		<body>
			<script src="https://code.jquery.com/jquery-2.2.4.min.js" integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44=" crossorigin="anonymous"></script>
			<h1>%s</h1>""" % (self.title, self.title)

	def _create_footer(self):
		return """
		</body>
	</html>"""

	def _create_info(self, info):
		return self._create_header() + """
		<p class="bg-info" style="margin:20px; padding:20px">%s</p>""" % info + self._create_footer()

	def _create_form(self):
		html_form = """
			<script>
				$(document).ready(function() {
					$('.form-control').focusout(function() {
						if(this.checkValidity()) {
							$(this).parent().parent().removeClass('has-error');
							if($(this).val().length !== 0) {
								$.post({
									url: 'update',
									data: {key: $(this).attr('name'), value: $(this).val()},
									mimeType: 'text/plain; charset=x-user-defined',
									dataType: 'text',
									success: function(data) {
										$('#info').text(data);
									}
								});
							}
						} else {
							$(this).parent().parent().addClass('has-error');
						}
					});
				});
			</script>
			<form class="form-horizontal" method="POST" action="/">"""

		for fieldset in self.form:
			html_form += """
				<fieldset>
					<legend>%s:</legend>""" % fieldset.legend
			for input_id, input in fieldset.inputs.items():
				input_params = 'id=%s name=%s class=form-control ' % (input.id, input.id)
				input_params += '' if input.hint is None else 'title="%s" ' % input.hint
				input_params += '' if input.placeholder is None else 'placeholder="%s" ' % input.placeholder
				input_params += '' if input.required is False else 'required '
				input_params += '' if input.pattern is None else 'pattern="%s" ' % input.pattern

				html_form += """
					<div class="form-group">
						<label class="control-label col-sm-2" for="%s">%s</label>
						<div class="input-group col-lg-10">
							""" % (input.id, input.name)

				if input.type == 'textarea':
					html_form += '<textarea %s>%s</textarea>' % (input_params, self.parameters[input.id])
				else:
					html_form += '<input type="%s" %s value="%s"/>' % (input.type, input_params, self.parameters[input.id])
				html_form += '' if input.unit is None else """
							<span class="input-group-addon">%s</span>""" % input.unit
				html_form += """
						</div>
					</div>"""

			html_form += """
				</fieldset>"""

		html_form += """
				<div class="form-group">
					<div class="col-sm-offset-2 col-sm-10">
						<button type="submit" class="btn btn-default">%s</button>
					</div>
				</div>
			</form>""" % self.button_name
		return self._create_header() + html_form + self._create_footer()

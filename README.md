# simpleWebInterface

*A really simple Python web server used to get several parameters from a web form.*

This package have only one function:

serve(*page title*, *form*, *send button name*, *callback function*)

Basic usage:

```python
#!/usr/bin/python3
# -*- coding: utf-8 -*

from simpleWebInterface import serve

# We describe the fieldsets and inputs of our form.
form = [
	{'legend':'Your informations',
	'inputs':[
		{'name':'name',  'label':'Your name', 'type':'text',     'tooltip':'Just enter your name.',     'placeholder':'Jean Martin',  'required':True},
		{'name':'age',                        'type':'number',   'tooltip':'How old are you',           'placeholder':'22',           'required':False}, # No label: default=name.title()
		{'name':'bio',   'label':'Biography', 'type':'textarea', 'tooltip':'What about you?',           'placeholder':'I am a chair collector.'} # No required: default=False
	]},
	{'legend':'Your object',
	'inputs':[
		{'name':'title',                                         'tooltip':'What do you want to sell?', 'placeholder':'A blue chair', 'required':True}, # No type: default=text
		{'name':'price',                      'type':'number',                                          'placeholder':'50',           'required':True}, # No tooltip: default=None
		{'name':'description',                'type':'textarea', 'tooltip':'Describe here the object'} # No placeholder: default=''
	]}]

# We define our callback function, wich is called when the user clicks to the Send button.
# handler: The BaseHTTPRequestHandler if you want to deal with it (ie. handler.wfile.write('something'))
# values: Our form, filled with the values set by the user.
# Return: the content eventually displayed on the web page when the user validate the form.
def callback(handler, values):
	'This function is called when the user click on the Send button.'
	name = values['name'].value
	response = 'Hello %s, so you want to sell %s for $%s?' \
		% (values['name'].value, values['title'].value, values['price'].value)
	print(response)
	return response

# Then we serve our form!
serve('A simple form with some parameters', form, 'Process parameters', callback)
```

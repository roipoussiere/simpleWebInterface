# simpleWebInterface

*A really simple Python web server used to get several parameters from a web form.*

This package have only one function:

serve(*page title*, *form*, *send button name*, *callback function*)

Basic usage:

```python
#!/usr/bin/python3
# -*- coding: utf-8 -*

from simpleWebInterface import Fieldset, Form

# We describe the fieldsets and inputs of our form.
infos = Fieldset('Your informations')
infos.add(name='Your name', type='text', hint='Only letters, between 3 and 20 chars. Ex: “Roger”', placeholder='Enter your name.', required=True, pattern='[A-Za-z]{3,20}')
infos.add(name='Age', type='number', hint='Enter a number. Ex: “42”', placeholder='How old are you?', required=False) # No id
infos.add(name='Biography', type='textarea', hint='All characters are autorized. Ex: “I am a chair collector.”', placeholder='What about you?') # No required: default=False

product = Fieldset('Your product')
product.add(name='Title', hint='All characters are autorized. Ex: “A blue chair.”', placeholder='What do you want to sell?', required=True), # No type: default=text
product.add(name='Price', type='number', unit='€', hint='Enter a number. Ex: “15”', required=True), # No placeholder: default=''
product.add(name='Description', type='textarea') # No hint: default='All characters are autorized.'

# We define how to do when the user update the form.
def on_update(key, value):
	"""This function is called each time the user update an input in the form (focus out).
	key: the id of the update input fieldset
	value: the content of the updated input field."""

	print('updated %s: %s' % (key, value))

# We define how to do when the user validate the form.
def on_valid(parameters):
	"""This function is called when tu user click on the Send button.
	parameters: A dictionnary containing all parameters.
	return: An information message eventually displayed instead of the form."""

	response = 'Hello %s, so you want to sell %s for $%s?' \
		% (parameters['your_name'], parameters['title'], parameters['price'])
	print(response)
	return response

# Then we serve our form!
form = Form([infos, product], on_update, on_valid, 'A wanderful web form')

```

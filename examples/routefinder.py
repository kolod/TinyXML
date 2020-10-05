# NextBus configurator.  Prompts user for transit agency, bus line,
# direction and stop, issues a string which can then be copied & pasted
# into the predictor program.  Not fancy, just uses text prompts,
# minimal error checking.

import requests
from xml.dom.minidom import parseString

# Open connection, issue request, read & parse XML response ------------------
def req(cmd):

	try:
		proxies = {
			"http": 'http://45.82.245.34:3128',  # USA
		}

		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.68"
		}

		url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=' + cmd
		print('Request: {0}'.format(url))

		response = requests.get(url, proxies = proxies, headers = headers)
		if response.status_code == 200:
			xml = parseString(response.text)
			return xml

		else:
			print('Error: {0}'.format(response.status_code))
			exit(1)

	except requests.exceptions.HTTPError as e:
		print('Error: {0}'.format(e))
		exit(1)

	except requests.exceptions.TooManyRedirects as e:
		print('Error: {0}'.format(e))
		exit(1)


# Prompt user for a number in a given range ----------------------------------
def getNum(prompt, n):
	while True:
		nb = input('Enter {0} 0-{1}: '.format(prompt, n - 1))
		try:                 x = int(nb)
		except ValueError:   continue    # Ignore non-numbers
		if x >= 0 and x < n: return x    # and out-of-range values

# Main application -----------------------------------------------------------

def main():
	# Get list of transit agencies, prompt user for selection, get agency tag.
	dom       = req('agencyList')
	elements  = dom.getElementsByTagName('agency')
	print('TRANSIT AGENCIES:')
	for i, item in enumerate(elements):
		print('{0}) {1}'.format(i, item.getAttribute('title')))
	n         = getNum('transit agency', len(elements))
	agencyTag = elements[n].getAttribute('tag')

	# Get list of routes for selected agency, prompt user, get route tag.
	dom       = req('routeList&a=' + agencyTag)
	elements  = dom.getElementsByTagName('route')
	print('\nROUTES:')
	for i, item in enumerate(elements):
		print('{0}) {1}'.format(i, item.getAttribute('title')))
	n         = getNum('route', len(elements))
	routeTag  = elements[n].getAttribute('tag')

	# Get list of directions for selected agency & route, prompt user...
	dom       = req('routeConfig&a=' + agencyTag + '&r=' + routeTag)
	elements  = dom.getElementsByTagName('direction')
	print('\nDIRECTIONS:')
	for i, item in enumerate(elements):
		print('{0}) {1}'.format(i, item.getAttribute('title')))
	n         = getNum('direction', len(elements))
	dirTitle  = elements[n].getAttribute('title') # Save for later
	# ...then get list of stop numbers and descriptions -- these are
	# nested in different parts of the XML and must be cross-referenced
	stopNums  = elements[n].getElementsByTagName('stop')
	stopDescs = dom.getElementsByTagName('stop')

	# Cross-reference stop numbers and descriptions to provide a readable
	# list of available stops for selected agency, route & direction.
	# Prompt user for stop number and get corresponding stop tag.
	print('\nSTOPS:')
	for i, item in enumerate(stopNums):
		stopNumTag = item.getAttribute('tag')
		for d in stopDescs:
			stopDescTag = d.getAttribute('tag')
			if stopNumTag == stopDescTag:
				print('{0}) {1}'.format(i, d.getAttribute('title')))
				break
	n         = getNum('stop', len(stopNums))
	stopTag   = stopNums[n].getAttribute('tag')

	# The prediction server wants the stop tag, NOT the stop ID, not sure
	# what's up with that.

	print('\nCOPY/PASTE INTO ARDUINO SKETCH:')
	print('  {{ 0x70, "{0}", "{1}", "{2}" }}, // {3}'.format(agencyTag, routeTag, stopTag, dirTitle))


if __name__ == "__main__" :
	main()
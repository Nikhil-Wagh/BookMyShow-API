from flask import Flask, redirect, abort, request, jsonify
from requests import get
from bs4 import BeautifulSoup

app = Flask(__name__)

baseUrl = "https://in.bookmyshow.com"

@app.route('/')
def hello_world():
	return 'BookMyShow API'


@app.errorhandler(404)
def pageNotFound(e):
	print(e)
	return "Error 404, Page not found."


@app.route('/<city>/', methods=["GET"])
def getNowShowing(city):
	event = "movies"
	if 'event' in request.args:
		event = request.args.get('event')
	# dimensions = []
	url = "https://in.bookmyshow.com/{city}/{event}".format(city=city.lower(), event=event.lower())
	print(url)
	try:
		bmsNowShowingContent = get(url)
	except Exception as e:
		print('Exception Occurred: ', e)
		return 'Could not reach BookMyShow.com'
	else:
		# print(bmsNowShowingContent.reason)
		if bmsNowShowingContent.status_code == 404:
			abort(404, "City/Event not supported")
		# raise ValueError('City not supported')
		else:
			soup = BeautifulSoup(bmsNowShowingContent.text, 'html5lib')
			movieUrls = {}
			for tag in soup.find_all("div", {"class": "movie-card-container"}):
				img = tag.find("img", {"class": "__poster __animated"})
				movie = {
					'name': img['alt'],
					'booking_url': tag.find('a', recursive=True)['href'],
					'image_url': img['data-src'],
					'language': tag['data-language-filter'][1:].split('|'),
					'dimensions': tag['data-dimension-filter'][1:].split('|')
				}
				movieUrls[movie['name']] = movie
			if len(movieUrls) <= 0:
				raise Exception('Data not received from BookMyShow.com')
			return jsonify(movieUrls)




if __name__ == '__main__':
	app.run()

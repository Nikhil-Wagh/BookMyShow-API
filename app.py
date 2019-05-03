from bs4 import BeautifulSoup
from flask import Flask, abort, request, jsonify
from requests import get
from json import loads

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

baseUrl = "https://in.bookmyshow.com"


@app.route('/')
def hello_world():
	return 'BookMyShow API'


@app.errorhandler(404)
def pageNotFound(e):
	print(e)
	return "Error 404, Page not found."


@app.route('/<city>/', methods=["GET", "POST"])
def getNowShowing(city):
	# event = request.form.get('event')
	# if event is None:
	# 	event = "movies"
	event = "Movies"
	data = loads(request.data)
	dimensions = data['dimensions']
	languages = data['languages']
	url = "https://in.bookmyshow.com/{city}/{event}".format(city=city.lower(), event=event.lower())
	try:
		bmsNowShowingContent = get(url)
	except Exception as e:
		print('Exception Occurred: ', e)
		return 'Could not reach BookMyShow.com'
	else:
		# print(bmsNowShowingContent.reason)
		if bmsNowShowingContent.status_code == 404:
			abort(404, "City/Event not supported")
		else:
			soup = BeautifulSoup(bmsNowShowingContent.text, 'html5lib')
			movieUrls = {}
			for tag in soup.find_all("div", {"class": "movie-card-container"}):
				img = tag.find("img", {"class": "__poster __animated"})
				movie = {
					'name': img['alt'],
					'booking_url': tag.find('a', recursive=True)['href'],
					'image_url': img['data-src'],
					'languages': tag['data-language-filter'][1:].split('|'),
					'dimensions': tag['data-dimension-filter'][1:].split('|')
				}
				if len(dimensions) > 0:
					if not any(dimen in movie['dimensions'] for dimen in dimensions):
						continue
				if len(languages) > 0:
					if not any(lang in movie['languages'] for lang in languages):
						continue
				movieUrls[movie['name']] = movie
			if len(movieUrls) <= 0:
				raise Exception('Data not received from BookMyShow.com')
			return jsonify(movieUrls)


if __name__ == '__main__':
	app.run()

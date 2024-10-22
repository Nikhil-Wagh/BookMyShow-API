from bs4 import BeautifulSoup
from flask import Flask, abort, request, jsonify
from requests import get
from json import loads

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config["DEBUG"] = True

baseUrl = "https://in.bookmyshow.com"


@app.route('/')
def hello_world():
	return 'BookMyShow API'


@app.errorhandler(404)
def pageNotFound(e):
	print(e)
	return "Error 404, Page not found."


@app.route('/<city>/', methods=["GET", "POST"])
def sendNowShowing(city):
	event = "Movies"
	data = loads(request.data)
	dimensions = data.get('dimensions')
	languages = data.get('languages')
	return jsonify(getNowShowing(city, event, languages, dimensions))


def getNowShowing(city, event, languages=None, dimensions=None):
	url = "https://in.bookmyshow.com/{city}/{event}".format(city=city.lower(), event=event.lower())
	try:
		bmsNowShowingContent = get(url)
	except Exception as e:
		print('Exception Occurred: ', e)
		return 'Could not reach BookMyShow.com'
	else:
		print(bmsNowShowingContent.reason)
		if bmsNowShowingContent.status_code == 404:
			abort(404, "City/Event not supported")
		else:
			soup = BeautifulSoup(bmsNowShowingContent.text, 'html5lib')
			movieUrls = {}
			for tag in soup.find_all("div", {"class": "movie-card-container"}):
				img = tag.find("img", {"class": "__poster __animated"})
				movie = {
					'name': img['alt'],
					'movieUrl': tag.find('a', recursive=True)['href'],
					'imageUrl': img['data-src'],
					'languages': tag['data-language-filter'][1:].split('|'),
					'dimensions': tag['data-dimension-filter'][1:].split('|')
				}
				if dimensions is not None:
					if not any(dimen in movie['dimensions'] for dimen in dimensions):
						continue
				if languages is not None:
					if not any(lang in movie['languages'] for lang in languages):
						continue
				movieUrls[movie['name']] = movie
			if len(movieUrls) <= 0:
				raise Exception('Data not received from BookMyShow.com')
			return movieUrls


def getVenueDataWithUrl(url):
	print(url)
	theatres_page_content = get(url)
	soup = BeautifulSoup(theatres_page_content.text, 'html5lib')
	print(soup.title.string)

	venue_data = []
	venues = soup.find("ul", {"id": "venuelist"})
	for venue in venues.find_all("li", {"class": "list"}):
		venue_name = venue.find("a", {"class": "__venue-name"}).text.strip()
		current_venue = {
			"name": venue_name,
			"timings": []
		}
		for timings in venue.find_all("a", {"class": "__showtime-link"}):
			current_timing = {
				"show_time": timings.text.strip()[:8],
				"seat_type": []
			}
			data_cat = loads(timings['data-cat-popup'])
			for seat in data_cat:
				current_seat = {
					"name": seat['desc'],
					"price": seat['price'],
					"availability": seat['availabilityText']
				}
				current_timing['seat_type'].append(current_seat)
			current_venue['timings'].append(current_timing)
		venue_data.append(current_venue)
	return jsonify({"details": venue_data})


def getVenueDataWithLangAndDimenUrl(langDimUrl, language, dimension):
	movieUrl = None
	print(langDimUrl)
	movie_page_content = get(langDimUrl)
	if movie_page_content.status_code != 200:
		raise Exception("Network error, please try again")

	soup = BeautifulSoup(movie_page_content.text, 'html5lib')

	tag = soup.find("div", {"id": "languageAndDimension"})
	for langs in tag.find_all("div", {"class": "format-heading"}):
		lang_from_site = langs.text.strip()
		dimensions = langs.next_sibling.next_sibling
		if lang_from_site == language:
			for dimen in dimensions.find_all("a", {"class": "dimension-pill"}):
				if dimen.text == dimension:
					movieUrl = dimen['href']
					break

	if movieUrl is None:
		return "Couldn't find the movie with given language and dimension."  # TODO: return with a proper json
	return getVenueDataWithUrl(baseUrl + movieUrl)


@app.route('/<city>/venues/', methods=["GET", "POST"])
def getVenuesData(city):
	requestData = loads(request.data)
	movieUrl = requestData.get('movieUrl')

	if movieUrl is not None:
		return getVenueDataWithUrl(movieUrl)

	dimension = requestData.get('dimension')
	language = requestData.get('language')
	langDimUrl = requestData.get('langDimUrl')

	if dimension is None:
		return "Dimension not provided"
	if language is None:
		return "Language not provided"

	if langDimUrl is not None:
		return getVenueDataWithLangAndDimenUrl(langDimUrl, language, dimension)

	movieName = requestData.get('movieName')
	if movieName is None:
		return "Movie name not provided"
	nowShowing = getNowShowing(city, "movies", [language], [dimension])
	# print(nowShowing)
	if movieName not in nowShowing:
		return jsonify({"available": nowShowing})
	return getVenueDataWithLangAndDimenUrl(baseUrl + nowShowing[movieName]['movieUrl'], language, dimension)


if __name__ == '__main__':
	app.run()

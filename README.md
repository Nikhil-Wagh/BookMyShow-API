### BookMyShow API

This API is created with Flask.

It supports following functions:
1. getMoviesNowShowing(city):
- To access this function hit the url: [https://yourserver.com/city/event](https://yourserver.com/city/event)
- It takes `city` as argument and returns a json of all the available movies in that city.
- Argument `event` is not supported yet, but will be available soon.
- To filter out results you could use `POST JSON(application/json)` parameters: `languages` and `dimensions`. Both should be list type object in json. 
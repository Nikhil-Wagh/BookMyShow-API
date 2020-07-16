# BookMyShow API

### This is not maintained now.

This API is created with Flask. It scrapes data from bookmyshow.com and provides the necessary data. No need of some special key, just hit the api to get results. 
*It is not live yet but will be soon.*

It supports following functions:
### 1. getMoviesNowShowing(city):
- To access this function hit the url: [https://yourserver.com/city/event](https://yourserver.com/city/event)
- It takes `city` as argument and returns a json of all the available movies in that city.
- Argument `event` is not supported yet, but will be available soon.
- To filter out results you could use `POST JSON(application/json)` parameters: `languages` and `dimensions`. Both should be list type object in json. 
### 2. getVenuesData(city):
- To access this function hit the url: [https://yourserver.com/city/venues](https://yourserver.com/city/venues)
- Returns: A JSON containing seat availability details of the venue in which the movie is showing.
```
{
    "details": [
        {
            "name": "<Venue Name>",
            "timings": [
                {
                    "show_time": "<Show Time>",
                    "seat_type": [
                        {
                            "name": "<Seat Type>",
                            "price": "<Price>",
                            "availability": "<Availbility = ['Available', 'Filling Fast', 'Sold Out']>"
                        }
                    ]
                }
            ]
        }
    ]
}
```
- Parameters:
    + `movieUrl`: A string URL of the **venues** page
    + `dimension`: A string `dimension` in which you want the result for that movie to be in(eg: *"2D", "3D"*, etc).
    + `language`: A string in which you want the results for that movie to be in (eg: *"English", "Hindi", "Marathi", "Tamil"*, etc.)
    + `langDimUrl`: A string URL of the page from where you select language and dimensions for that movie.
- It works with 3 different cases:
    #### 2.1 `movieUrl` is given (Fastest): 
     If the `movieUrl` is given it will directly show the result 
     ```
     {
        "movieUrl": "https://in.bookmyshow.com/buytickets/avengers-endgame-pune/movie-pune-ET00090482-MT/"
     }
     ```
    #### 2.2 `langDimUrl` is given (Intermediate): 
    It requires the `dimension` and `language` parameters to work properly.
    ```
    {
        "language": "English",
        "dimension": "3D",
        "langDimUrl": "https://in.bookmyshow.com/pune/movies/avengers-endgame/ET00090482"
    }
    ```
    To get these parameters first hit `/<city>/` with the `movieName`. Then hit `/<city>/venues` for venues data.
    #### 2.3 `movieName` is given (Slowest): 
    It requires exact `movieName`, `dimension` and `language` to work properly. 
    ```
    {
        "language": "English",
        "dimension": "3D",
        "movieName": "Avengers: Endgame"
    }
    ```
    
Feel free to contribute!!
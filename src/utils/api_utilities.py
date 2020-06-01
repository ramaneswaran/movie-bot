# This module contains functions to facilitate calls to OMDB API

def get_meta_data(imdb_id, key):
    '''
    This function returns metadata 
    Parameters:
    imdb_id (string) : The movie ID
    key (string) : The secret API key
    Return:
    tuple: containing title, year, runtime and poster
    '''
    try:
        url = 'http://www.omdbapi.com/?i=tt'+imdb_id+'&apikey='+key
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['Title'], data['Year'], data['Runtime'], data['Poster']
        else:
            return -1
    except Exception as error:
        return -1
    

def get_movie_detail(imdb_id, detail, key):
    '''
    This function returns the details of a movie
    the detail keyword can be 
    
    'Title', 'Year', 'Rated', 'Released', 'Runtime', 'Genre', 'Director', 'Writer', 
    'Actors', 'Plot', 'Language', 'Country', 'Awards', 'Poster', , 'Metascore', 
    'imdbRating', 'imdbVotes', 'imdbID'
    
    Parameters:
    imdb_id (string) : The movie ID
    detail (string): The detail to fetch
    key (string) : The secret API key
    Return:
    string: The detail fetched
    '''
    try:
        url = 'http://www.omdbapi.com/?i=tt'+imdb_id+'&apikey='+key
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if detail not in data:
                raise Exception("Invalid detail")
            return data[detail]
        else:
            return -1
    except Exception as error:
        print(error)
        return -1

def get_rating(imdb_id, key):
    '''
    This function returns ratings of a movie
    Parameters:
    imdb_id (string) : The movie ID
    key (string) : The secret API key
    Return:
    list: of ratings of form {name, rating}
    '''
    try:
        url = 'http://www.omdbapi.com/?i=tt'+imdb_id+'&apikey='+key
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['Ratings']
        else:
            return -1
    except Exception as error:
        print(error)
        return -1
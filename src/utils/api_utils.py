# This module contains functions to facilitate calls to OMDB API
import requests

def get_metadata(imdb_id, key):
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
        data = response.json()
        
        if data['Response'] != 'True':
            return False, None

    except Exception as error:
        return False, None
    
    finally:
        return True, data
    

def get_movie_detail(imdb_id, detail, key):
    '''
    This function returns the details of a movie
    the detail keyword can be 
    
    'Title', 'Year', 'Rated', 'Released', 'Runtime', 'Genre', 'Director', 'Writer', 
    'Actors', 'Plot', 'Language', 'Country', 'Awards', 'Poster', 'Metascore', 
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
        data = response.json()

        if data['Response'] != 'True':
            raise Exception("API call unsuccessfull")

    except Exception as error:
        print(error)
        return False, None
    finally:
        return True, data[detail]

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
        data = response.json()

        if data['Response'] != 'True':
            raise Exception("API call unsuccessfull")
    except Exception as error:
        print(error)
        return False, None
    finally:
        return True, data['Rating']

def get_plot(title, key):
    '''
    This function return plot of movie
    Parameters:
    imdb_id (string) : The movie ID
    key (string) : The secret API key
    Return:
    string: Plot of the movie 
    '''
    try:
        url = 'http://www.omdbapi.com/?t='+title+'&apikey='+key
        response = requests.get(url)
        data = response.json()

        if data['Response'] != 'True':
            raise Exception("API call unsuccessfull")
    
    except Exception as error:
        print(error)
        return False, None
    
    finally:
        return True, data['Plot']

import numpy as np 

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class Engine:
    '''
    Reccomendation engine of the bot
    '''
    def __init__(self, vectorizer, mov_matrix, rev_map, metadata):
        '''
        Constructor class for reccomendation engine class
        Parameters:
        vectorizer: tfidf vectorizer trained on dataset
        mov_matrix: tfidf matrix of the dataset
        rev_map: A reverse map from id to imdb.id
        '''

        #  Load the vectorizer
        self.vectorizer = vectorizer
        
        # Load the matrix
        self.matrix = mov_matrix
        
        # Load the reverse map
        self.rev_map = rev_map

        # Load metadata
        self.metadata = metadata

        # Movies list
        self.movies = metadata['original_title']
        
    def similar_movies(self, plot):
        '''
        This function returns a list of similar movies
        Parameters:
        plot: plot of the movie
        Return:
        list: top 5 similar movies
        '''
        # Vectorize the plot
        doc_vector = self.vectorizer.transform([plot])
        
        # Compute a similarity vector
        sim_vec = linear_kernel(self.matrix, doc_vector)
        
        # Get top 5 movies
        # sim_scores = list(enumerate(sim_vec))
        # sim_scores = sorted(sim_scores, key=lambda x:x[1], reverse=True)
        # sim_scores = sim_scores[1:6]
   

        # return [self.rev_map[movie[0]] for movie in sim_scores]

        idxs = np.argpartition(sim_vec.flatten(), -5)[-5:]

        return [self.rev_map[idx] for idx in idxs]

    def search_movie(self, title):
        movies = process.extract("batman", self.movies, scorer=fuzz.ratio)
        return movies[0][2]

    def get_plot(self, id):
        return self.metadata.iloc[id]['soup']
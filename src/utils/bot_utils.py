def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    '''
    This function builds menu
    '''
    menu = None
    try:
        
        menu = [buttons[i:i+n_cols] for i in range(0, len(buttons), n_cols)]

        if header_buttons:
            menu.insert(0, [header_buttons])
        if footer_buttons:
            menu.append([footer_buttons])
        
    except Exception as error:
        return False, None
    finally:    
        
        return True, menu

def create_user_state():
    return {'request':False, 'cur_id':None, 'movie_gen':None}

def get_movie_gen(self, movie_ids):
    '''
    This function returns a generator for movie IDs
    '''
    for imdb_id in movie_ids:
        yield(imdb_id)

def get_movie_title(doc):
    '''
    This function returns the movie title
    '''
    
    try:
        ent = doc.ents[0]
        title = ent.text 
    except Exception as error:
        return False, None
    finally:
        return True, title
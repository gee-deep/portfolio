import random

MOVIE_QUOTES = [
    {
        "quote": "Life is a movie; death is a photograph.",
        "author": "Susan Sontag"
    },
    {
        "quote": "Cinema is the most beautiful fraud in the world.",
        "author": "Jean-Luc Godard"
    },
    {
        "quote": "Movies touch our hearts and awaken our vision, and change the way we see things.",
        "author": "Martin Scorsese"
    },
    {
        "quote": "If it can be written, or thought, it can be filmed.",
        "author": "Stanley Kubrick"
    },
    {
        "quote": "Cinema is a matter of what's in the frame and what's out.",
        "author": "Martin Scorsese"
    }
]

BOOK_QUOTES = [
    {
        "quote": "A room without books is like a body without a soul.",
        "author": "Marcus Tullius Cicero"
    },
    {
        "quote": "Books are a uniquely portable magic.",
        "author": "Stephen King"
    },
    {
        "quote": "Reading is to the mind what exercise is to the body.",
        "author": "Joseph Addison"
    },
    {
        "quote": "There is no friend as loyal as a book.",
        "author": "Ernest Hemingway"
    },
    {
        "quote": "Books are mirrors: you only see in them what you already have inside you.",
        "author": "Carlos Ruiz Zafón"
    }
]

def get_random_quote(quote_type='book'):
    quotes = BOOK_QUOTES if quote_type == 'book' else MOVIE_QUOTES
    return random.choice(quotes) 
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from typing import Optional
from datetime import datetime

app = FastAPI()


class Book:
    def __init__(self, id, title, author, description, rating, publish_year):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.publish_year = publish_year


class BookRequest(BaseModel):
    id: Optional[int] = Field(
        description='ID is not needed on create', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    publish_year: int = Field(gt=1970, le=datetime.now().year)

    model_config = {
        'json_schema_extra': {
            'example': {
                'title': 'Harry Potter',
                'author': 'J.K.Rowling',
                'description': 'Lorem ipsum dolor',
                'rating': 5,
                'publish_year': 1997
            }
        }
    }


books = [
    Book(1, 'Atomic Habits', 'James Clear', 'Lorem ipsum dolor', 5, 2018),
    Book(2, 'Rich Dad Poor Dad', 'Robert Kiyosaki', 'Lorem ipsum dolor', 4, 1997),
    Book(3, 'The Almanack of Naval Ravikant',
         'Eric Jorgenson', 'Lorem ipsum dolor', 5, 2020),
    Book(4, 'Mindset', 'Carol S. Dweck', 'Lorem ipsum dolor', 4, 2006),
    Book(5, 'Think Like a Monk', 'Jay Shetty', 'Lorem ipsum dolor', 4, 2020),
    Book(6, '8 Rules of Love', 'Jay Shetty', 'Lorem ipsum dolor', 4, 2023)
]


# Assigns an auto increment ID to the book based on the last book's ID
def find_book_id(book: Book):
    book.id = 1 if len(books) == 0 else books[-1].id + 1
    return book


@app.get('/books', status_code=status.HTTP_200_OK)
async def read_all_books():
    return books


@app.get('/books/{book_id}', status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Book not found')


@app.get('/books/', status_code=status.HTTP_200_OK)
async def read_book_by_ratig(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in books:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return


@app.get('/book/publish-year/', status_code=status.HTTP_200_OK)
async def read_book_by_year(publish_year: int = Query(gt=1970, le=datetime.now().year)):
    books_to_return = []
    for book in books:
        if book.publish_year == publish_year:
            books_to_return.append(book)
    return books_to_return


@app.post('/books/create-book', status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    books.append(find_book_id(book_request))


@app.put('/books/update-book', status_code=status.HTTP_204_NO_CONTENT)
async def update_book(update_book: BookRequest):
    for i, book in enumerate(books):
        if book.id == update_book.id:
            books[i] = update_book
            return {'message': 'Book updated successfully'}
    raise HTTPException(status_code=404, detail='Book not found')


@app.delete('/books/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    for i, book in enumerate(books):
        if book.id == book_id:
            books.pop(i)
            return {'message': 'Book deleted successfully'}
    raise HTTPException(status_code=404, detail='Book not found')

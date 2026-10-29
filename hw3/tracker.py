# Трекер книг

books = []          # list: все книги
books_by_id = {}    # dict: поиск книги по id
authors = set()     # set: уникальные авторы
read_ids = set()    # set: id прочитанных книг


def add_book(book_id, title, author, year):
    if book_id in books_by_id:
        return False
    book = (book_id, title, author, year)   # tuple: одна запись
    books.append(book)
    books_by_id[book_id] = book
    authors.add(author)
    return True


def find_book(book_id):
    return books_by_id.get(book_id)


def mark_as_read(book_id):
    if book_id not in books_by_id:
        return False
    read_ids.add(book_id)
    return True


def remove_book(book_id):
    book = books_by_id.pop(book_id, None)
    if book is None:
        return False
    books.remove(book)
    read_ids.discard(book_id)
    authors.clear()
    authors.update(b[2] for b in books)
    return True


def get_all_books():
    return list(books)   # копия, а не сам список


def get_unread_books():
    return [b for b in books if b[0] not in read_ids]


def main():
    add_book(1, "Мастер и Маргарита", "Булгаков", 1967)
    add_book(2, "Белая гвардия", "Булгаков", 1925)
    add_book(3, "1984", "Оруэлл", 1949)

    print("Дубликат добавился?", add_book(1, "Другая книга", "Кто-то", 2000))
    print("Книга 3:", find_book(3))

    mark_as_read(1)
    print("Непрочитанные:", get_unread_books())

    remove_book(3)
    print("Авторы после удаления:", authors)


if __name__ == "__main__":
    main()

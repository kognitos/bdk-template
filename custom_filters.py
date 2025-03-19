from jinja2.ext import Extension


def ensure_ends_with_book(value):
    while value.lower().endswith("book"):
        value = value[:-4]
    return value + "Book"

def remove_book_prefix(value):
    while value.lower().startswith("book_"):
        value = value[5:]
    return value

def soft_capitalize(values):
    ret = []
    for val in values:
        if val:
            ret.append(val[0].upper() + val[1:])
    return ret

def split_by(value, divisor):
    return value.split(divisor)

class CustomFiltersExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.filters['ensure_ends_with_book'] = ensure_ends_with_book
        environment.filters['remove_book_prefix'] = remove_book_prefix
        environment.filters['soft_capitalize'] = soft_capitalize
        environment.filters['split_by'] = split_by




class Rating:
    def __init__(self, rating: int):
        self.rating = rating

    def render_stars_html(self):
        result = ''
        for i in range(self.rating):
            result += '<img src="/static/img/star.svg" alt="">\n'
        for i in range(5 - self.rating):
            result += '<img src="/static/img/star-empty.svg" alt="">\n'
        return result

    def __str__(self):
        return str(self.rating) if self.rating > 0 else 'No rating'
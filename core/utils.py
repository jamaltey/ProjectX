isEmpty = lambda string: str(string).isspace() or not string or string == 'None'

class Rating:
    def __init__(self, rating=0):
        if not rating:
            self.rating = 0
        else:
            rating = int(rating)
            if rating <= 5:
                self.rating = rating
            else:
                self.rating = 5

    def render_stars_html(self):
        return (
            '<img src="/static/img/star.svg" alt="⭐️">\n' * self.rating
            +
            '<img src="/static/img/star-empty.svg" alt="⭐️">\n' * (5 - self.rating)
        )

    def __repr__(self) -> str:
        return f'<Rating object "{str(self)}">'

    def __str__(self):
        return str(self.rating) if self.rating else 'No rating'

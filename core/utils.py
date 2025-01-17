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
            '<i class="fa-sharp fa-solid fa-star"></i>\n' * self.rating
            +
            '<i class="fa-regular fa-star"></i>\n' * (5 - self.rating)
        )

    def __repr__(self) -> str:
        return f'<Rating object "{str(self)}">'

    def __str__(self):
        return str(self.rating) if self.rating else 'No rating'

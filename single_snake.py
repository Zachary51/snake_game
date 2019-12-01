class Snake:
    def __init__(self, pos, rows, cols):
        self.rows, self.cols = rows, cols
        self.body = [pos]
        self.dx, self.dy = 0, 1

    def head(self):
        return self.body[0]

class Choice:

    def __init__(self, text, correct):
        self.text = text
        self.correct = correct

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, val):
        if len(val) == 0:
            raise ValueError("invalid text")

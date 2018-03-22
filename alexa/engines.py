class EmotionEngine:
    def __init__(self):
        self.default_text = 'I am Emotional Engine'
        self.is_done = False

    def io(self, request):
        self.is_done = True
        return self.default_text

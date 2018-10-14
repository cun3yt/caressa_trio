class Intent:
    def __init__(self, name, samples):
        self.name = name
        self.samples = samples

    def is_match(self, text):
        return text in self.samples


yes_intent = Intent(name='yes',
                    samples=['yes',
                             'of course',
                             'ok',
                             'o.k.',
                             'okey',
                             'sure',
                             'why not',
                             'definitely',
                             'for sure',
                             'yeah',
                             'yea',
                             'hell yes',
                             'hell yeah',
                             'good call',
                             'alright',
                             'most definitely', ])

no_intent = Intent(name='no',
                   samples=['no',
                            'no thanks',
                            'nope',
                            'no way',
                            'there is no way',
                            'hell no',
                            'of course no',
                            'of course not',
                            'definitely no',
                            'definitely not', ])

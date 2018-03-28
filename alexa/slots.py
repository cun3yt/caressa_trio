import json


class SlotTypeValue:
    def __init__(self, value, synonyms=None):
        self.value = value
        self.synonyms = synonyms

    def render(self, render_type='json'):
        dict_repr = {
            "name": {
                "value": self.value
            }
        }

        if self.synonyms:
            dict_repr['synonyms'] = self.synonyms

        return json.dumps(dict_repr) if render_type == 'json' else dict_repr


class SlotType:
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def render(self, render_type='json'):
        dict_repr = {
            "name": self.name,
            "values": [value.render(render_type='dict') for value in self.values],
        }
        return json.dumps(dict_repr) if render_type == 'json' else dict_repr


class Slot:
    def __init__(self, name, slot_type: SlotType):
        self.name = name
        self.slot_type = slot_type

    def render(self, render_type='json'):
        dict_repr = {
            "name": self.name,
            "type": self.slot_type.name
        }
        return json.dumps(dict_repr) if render_type == 'json' else dict_repr

    def __repr__(self):
        return "{{{}}}".format(self.name)


class SlotTypeFeelingGood(SlotType):
    def __init__(self):
        name = 'slot_type_feeling_good'
        values = {
            "name": {
                "value": "good",
                "synonyms": [
                    "incredible",
                    "great",
                    "awesome",
                ]
            }
        }
        super(SlotTypeFeelingGood, self).__init__(name, values)


class SlotFeelingGood(Slot):
    def __init__(self):
        super(SlotFeelingGood, self).__init__(name='feeling_good_slot', slot_type=SlotTypeFeelingGood())

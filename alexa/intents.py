from random import sample
from alexa.slots import SlotFeelingGood


class Intent:
    def __init__(self, name, response_set, slots=None, follow_engine=None, samples=None, process_fn=None,
                 question=None, end_session=False, **kwargs):
        self.name = name
        self.response_set = response_set    # either function or list of strings
        self.slots = slots
        self.follow_engine = follow_engine  # todo not in use yet
        self.samples = samples
        self.process_fn = process_fn
        self.question = question
        self.end_session = end_session
        self.engine_session = kwargs.get('engine_session', None)    # todo is this in use? Delete if not.
        self.profile_builder = kwargs.get('profile_builder', None)

    @classmethod
    def intent_identifier(cls):
        return "intent-identifier"

    def is_end_state(self):
        # is leaf?  does the engine session end?
        return not self.question

    def get_random_response(self):
        if type(self.response_set) is list:
            return sample(self.response_set, 1)[0]
        return self.response_set()


class GoodIntent(Intent):
    def __init__(self, process_fn=None, question=None, response_set=None):
        name = GoodIntent.intent_identifier()
        slot_feeling_good = SlotFeelingGood()
        default_response_set = [
            "that's good to hear.",
            "that's awesome!",
        ]
        samples = [
            "I feel {feeling_good}".format(feeling_good=slot_feeling_good),
            "I am feeling {feeling_good}".format(feeling_good=slot_feeling_good),
            "great",
            "the best",
            "good",
        ]
        response_set = response_set if response_set else default_response_set
        slots = [
            slot_feeling_good,
        ]
        super(GoodIntent, self).__init__(name=name, response_set=response_set, samples=samples, slots=slots,
                                         process_fn=process_fn, question=question)

    def get_random_response(self):
        return sample(self.response_set, 1)[0]

    @classmethod
    def intent_identifier(cls):
        return 'good_intent'


class BadIntent(Intent):
    @classmethod
    def intent_identifier(cls):
        return 'bad_intent'

    def __init__(self, slots=None, process_fn=None, question=None, response_set=None):
        name = self.intent_identifier()
        default_response_set = [
            "I am sorry to hear.",
            "Ah, that's bad!",
            "Oh, I'm sorry",
        ]
        samples = [
            "I am feeling {feeling_bad_slot}",
            "I feel {feeling_bad_slot}",
            "sad",
            "terrible",
            "worse",
            "bad",
        ]
        response_set = response_set if response_set else default_response_set
        super(BadIntent, self).__init__(name=name, response_set=response_set, samples=samples, slots=slots,
                                        process_fn=process_fn, question=question)


class YesIntent(Intent):
    @classmethod
    def intent_identifier(cls):
        return 'yes_intent'

    def __init__(self, slots=None, process_fn=None, question=None, response_set=None, **kwargs):
        name = self.intent_identifier()
        default_response_set = [
            "Good!",
        ]
        samples = [
            "yep",
            "yeah",
            "good call",
            "of course",
            "sure",
            "yes",
        ]
        response_set = response_set if response_set else default_response_set
        super(YesIntent, self).__init__(name=name, response_set=response_set, samples=samples, slots=slots,
                                        process_fn=process_fn, question=question, **kwargs)


class NoIntent(Intent):
    @classmethod
    def intent_identifier(cls):
        return 'no_intent'

    def __init__(self, slots=None, process_fn=None, question=None, response_set=None):
        name = self.intent_identifier()
        default_response_set = [
            'OK',
            'No problem',
        ]
        samples = [
            "nope",
            "of course not",
            "hell no",
            "no",
        ]
        response_set = response_set if response_set else default_response_set
        super(NoIntent, self).__init__(name=name, response_set=response_set, samples=samples, slots=slots,
                                       process_fn=process_fn, question=question)


class StopIntent(Intent):
    @classmethod
    def intent_identifier(cls):
        return 'stop_intent'

    def __init__(self, slots=None, process_fn=None, question=None, response_set=None, end_session=True):
        name = self.intent_identifier()
        default_response_set = [
            'Later',
            'Goodbye',
        ]
        samples = [
            "stop",
            "off",
            "shut up",
            "go away",
        ]
        response_set = response_set if response_set else default_response_set
        super(StopIntent, self).__init__(name=name, response_set=response_set, samples=samples, slots=slots,
                                         process_fn=process_fn, question=question, end_session=end_session)


class BloodPressureIntent(Intent):
    @classmethod
    def intent_identifier(cls):
        return 'blood_pressure_intent'

    def __init__(self, slots=None, process_fn=None, question=None, response_set=None):
        name = self.intent_identifier()
        default_response_set = [
            "Thanks, I jotted them down.",
            "Alright!",
        ]
        samples = [
            "it is {systolic_slot} over {diastolic_slot}",
            "{diastolic_slot} over Systolic {systolic_slot}",
            "Diastolic {diastolic_slot} over {systolic_slot}",
            "{systolic_slot} over Diastolic {diastolic_slot}",
            "Systolic {systolic_slot} over {diastolic_slot}",
            "Diastolic {diastolic_slot} over Systolic {systolic_slot}",
            "Systolic {systolic_slot} over Diastolic {diastolic_slot}",
            "{systolic_slot} over {diastolic_slot}",
        ]
        response_set = response_set if response_set else default_response_set
        super(BloodPressureIntent, self).__init__(name=name, response_set=response_set, samples=samples, slots=slots,
                                                  process_fn=process_fn, question=question)


class WeightIntent(Intent):
    @classmethod
    def intent_identifier(cls):
        return 'weight_intent'

    def __init__(self, slots=None, process_fn=None, question=None, response_set=None):
        name = self.intent_identifier()
        default_response_set = [
            "Thanks for letting me know your weight measure, I jotted it down.",
            "Awesome, I wrote your weight measure down.",
            "Thanks for letting me know.",
            "Alright, thank you!",
            "Thank you very much!",
        ]
        samples = [
            "{weight_slot}",
            "{weight_slot} pounds",
        ]
        response_set = response_set if response_set else default_response_set
        super(WeightIntent, self).__init__(name=name, response_set=response_set, samples=samples, slots=slots,
                                           process_fn=process_fn, question=question)

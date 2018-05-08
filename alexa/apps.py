from django.apps import AppConfig


class AlexaConfig(AppConfig):
    name = 'alexa'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('UserActOnContent'))
        registry.register(self.get_model('Joke'))
        registry.register(self.get_model('User'))

from django.apps import AppConfig


class ActionsConfig(AppConfig):
    name = 'actions'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('UserPost'))
        registry.register(self.get_model('ActionGeneric'))

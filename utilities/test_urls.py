from django.urls import path


test_urls = [
    path('test/url/', lambda request: None, name='test-url'),
    path('test/url/<int:pk>/', lambda request: None, name='test-url-pk'),
]

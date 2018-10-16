from django.contrib import admin


def get_admin():
    admin.site.site_header = 'Caressa Admin'
    admin.site.site_title = 'Caressa Administration'
    admin.site.index_title = 'Welcome to Caressa Admin Page'
    return admin

from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Super_user)
admin.site.register(Report)
admin.site.register(Document)
admin.site.register(Category)
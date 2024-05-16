from django.contrib import admin
from requestTour.models import AddRequest, EditRequest, CancelRequest, Request

# Register your models here.
admin.site.register(Request)
admin.site.register(AddRequest)
admin.site.register(EditRequest)
admin.site.register(CancelRequest)
from django.contrib import admin
from .models import Image, Participant, Response, AdviceStartTime, AdviceEndTime

# Register your models
admin.site.register(Image)
admin.site.register(Participant)
admin.site.register(Response)
admin.site.register(AdviceStartTime)
admin.site.register(AdviceEndTime)


# Register your models here.

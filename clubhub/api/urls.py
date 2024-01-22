from django.urls import path



from . import views
from . import admin


urlpatterns = [
    path("", views.index, name="index"),
]

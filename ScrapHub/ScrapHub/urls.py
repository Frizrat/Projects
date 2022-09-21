from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index, name='Index'),
    path('ScrapMain/', views.ScrapMain),
    path('ScrapSearch/', views.ScrapSearch),
    path('ScrapInfo/', views.ScrapInfo),
    path('ScrapVideo/', views.ScrapVideo),
    path('ScrapImage/', views.ScrapImage),
    path('ScrapGenre/', views.ScrapGenre),

    path('admin/', admin.site.urls),
]

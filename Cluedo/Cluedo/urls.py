from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('changeIndex/', views.changeIndex),
    path('chercheIndex/', views.chercheIndex),
    path('ajout/', views.ajout),
    path('ajoutPOST/', views.ajoutPOST),
    path('parcoursLargeur/', views.parcoursLargeur),
    path('parcoursPrefixe/', views.parcoursPrefixe),
    path('parcoursInfixe/', views.parcoursInfixe),
    path('parcoursSuffixe/', views.parcoursSuffixe),
    path('graphviz/', views.graphviz),

    path('admin/', admin.site.urls),
]

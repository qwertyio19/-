from django.urls import path, include 
from app.pro_activity.views import ActivityViewViewSet, TypeActivityViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'ativity', ActivityViewViewSet, basename='ativity')
router.register(r'type_activity', TypeActivityViewSet, basename='typeactivityViewSet')

urlpatterns = [

]

urlpatterns += router.urls

from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("checkout/", views.checkout, name="CheckOut"),
    path("products/<int:myid>", views.productView, name="view"),
    path('search/',views.search,name='search')
]

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
    path("new", views.new, name="new"),
    path("submit",views.submit,name="submit"),
    path("listings/<int:id>",views.listings,name="listings"),
    path("bidSubmit/<int:listing_id>",views.bidSubmit,name="bidSubmit"),
    path("commentSubmit/<int:listing_id>",views.commentSubmit,name="commentSubmit"),
    path("addWatchList/<int:listing_id>",views.addWatchList,name="addWatchList"),
    path("removeWatchList/<int:listing_id>",views.removeWatchList,name="removeWatchList"),
    path("watchlist/<str:username>",views.watchlist,name="watchlist"),
    path("closebid/<int:listing_id>",views.closebid,name="closebid"),
    path("winnings",views.winnings,name="winnings")
]

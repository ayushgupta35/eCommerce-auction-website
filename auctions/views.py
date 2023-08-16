from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .models import User, Bid, Listing, Comment, Watchlist, Closedbid, All_Listings

def index(request):
    items=Listing.objects.all()
    items = [ele for ele in reversed(items)]
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        watchcount = len(w)
        if len(w) == 0:
            watchcount = 0
    except:
        watchcount = 0
    return render(request, "auctions/index.html",{
        "items":items,
        "watchcount":watchcount
    })

@login_required
def categories(request):
    items = Listing.objects.raw("SELECT * FROM auctions_listing GROUP BY category")
    items = [ele for ele in reversed(items)]
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        watchcount = len(w)
        if len(w) == 0:
            watchcount = 0
    except:
        watchcount = 0
    return render(request,"auctions/categories.html",{
        "items": items,
        "watchcount":watchcount
    })

@login_required
def category(request,category):
    categoryitems = Listing.objects.filter(category=category)
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        watchcount = len(w)
        if len(w) == 0:
            watchcount = 0
    except:
        watchcount = 0
    return render(request,"auctions/category.html",{
        "items":categoryitems,
        "category":category,
        "watchcount":watchcount
    })

@login_required
def new(request):
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        watchcount = len(w)
        if len(w) == 0:
            watchcount = 0
    except:
        watchcount = 0
    return render(request,"auctions/new.html",{
        "watchcount":watchcount
    })

@login_required
def submit(request):
    if request.method == "POST":
        listing_table = Listing()
        now = datetime.now()
        dt = now.strftime(" %d %B %Y %X ")
        listing_table.owner = request.user.username
        listing_table.title = request.POST.get('title')
        listing_table.description = request.POST.get('description')
        listing_table.price = request.POST.get('price')
        listing_table.category = request.POST.get('category')
        if request.POST.get('link'):
            listing_table.link = request.POST.get('link')
        else :
            listing_table.link = "https://www.freeiconspng.com/thumbs/no-image-icon/no-image-icon-6.png"
        listing_table.time = dt
        listing_table.save()
        all = All_Listings()
        items = Listing.objects.all()
        for i in items:
            try:
                if All_Listings.objects.get(listing_id=i.id):
                    pass
            except:
                all.listing_id=i.id
                all.title = i.title
                all.description = i.description
                all.link = i.link
                all.save()

        return redirect('index')
    else:
        return redirect('index')

@login_required
def listings(request,id):
    try:
        item = Listing.objects.get(id=id)
    except:
        return redirect('index')
    try:
        comments = Comment.objects.filter(listing_id=id)
    except:
        comments = None
    if request.user.username:
        try:
            if Watchlist.objects.get(user=request.user.username,listing_id=id):
                added=True
        except:
            added = False
        try:
            listings = Listing.objects.get(id=id)
            if listings.owner == request.user.username :
                owner = True
            else:
                owner = False
        except:
            return redirect('index')
    else:
        added = False
        owner = False
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        watchcount = len(w)
        if len(w) == 0:
            watchcount = 0
    except:
        watchcount = 0
    return render(request,"auctions/listings.html",{
        "item":item,
        "error":request.COOKIES.get('error'),
        "errorgreen":request.COOKIES.get('errorgreen'),
        "comments":comments,
        "added":added,
        "owner":owner,
        "watchcount":watchcount
    })

@login_required
def bidSubmit(request,listing_id):
    current_bid = Listing.objects.get(id=listing_id)
    current_bid = current_bid.price
    if request.method == "POST":
        user_bid = int(request.POST.get("bid"))
        if user_bid > current_bid:
            listing_items = Listing.objects.get(id=listing_id)
            listing_items.price = user_bid
            listing_items.save()
            try:
                if Bid.objects.filter(id=listing_id):
                    bid_row = Bid.objects.filter(id=listing_id)
                    bid_row.delete()
                bid_table = Bid()
                bid_table.user=request.user.username
                bid_table.title = listing_items.title
                bid_table.listing_id = listing_id
                bid_table.bid = user_bid
                bid_table.save()
                
            except:
                bid_table = Bid()
                bid_table.user=request.user.username
                bid_table.title = listing_items.title
                bid_table.listing_id = listing_id
                bid_table.bid = user_bid
                bid_table.save()
            response = redirect('listings',id=listing_id)
            response.set_cookie('errorgreen','Successful Placed Bid!',max_age=3)
            return response
        else :
            response = redirect('listings',id=listing_id)
            response.set_cookie('error','Bid should be greater than current bid',max_age=3)
            return response
    else:
        return redirect('index')

@login_required
def commentSubmit(request,listing_id):
    if request.method == "POST":
        now = datetime.now()
        date = now.strftime(" %d %B %Y %X ")
        comment = Comment()
        comment.comment = request.POST.get('comment')
        comment.user = request.user.username
        comment.time = date
        comment.listing_id = listing_id
        comment.save()
        return redirect('listings',id=listing_id)
    else :
        return redirect('index')

@login_required
def addWatchList(request,listing_id):
    if request.user.username:
        w = Watchlist()
        w.user = request.user.username
        w.listing_id = listing_id
        w.save()
        return redirect('listings',id=listing_id)
    else:
        return redirect('index')

@login_required
def removeWatchList(request,listing_id):
    if request.user.username:
        try:
            w = Watchlist.objects.get(user=request.user.username,listing_id=listing_id)
            w.delete()
            return redirect('listings',id=listing_id)
        except:
            return redirect('listings',id=listing_id)
    else:
        return redirect('index')

@login_required
def watchlist(request,username):
    if request.user.username:
        try:
            w = Watchlist.objects.filter(user=username)
            items = []
            for i in w:
                items.append(Listing.objects.filter(id=i.listing_id))
            items = [ele for ele in reversed(items)]
            try:
                w = Watchlist.objects.filter(user=request.user.username)
                watchcount = len(w)
                if len(w) == 0:
                    watchcount = 0
            except:
                watchcount = 0
            return render(request,"auctions/watchlist.html",{
                "items":items,
                "watchcount":watchcount
            })
        except:
            try:
                w = Watchlist.objects.filter(user=request.user.username)
                watchcount = len(w)
                if len(w) == 0:
                    watchcount = 0
            except:
                watchcount = 0
            return render(request,"auctions/watchlist.html",{
                "items":None,
                "watchcount":watchcount
            })
    else:
        return redirect('index')

@login_required
def closebid(request,listing_id):
    if request.user.username:
        try:
            listing_row = Listing.objects.get(id=listing_id)
        except:
            return redirect('index')
        close_bid = Closedbid()
        title = listing_row.title
        close_bid.owner = listing_row.owner
        close_bid.listing_id = listing_id
        try:
            bid_row = Bid.objects.get(listing_id=listing_id,bid=listing_row.price)
            close_bid.winner = bid_row.user
            close_bid.winprice = bid_row.bid
            close_bid.save()
            bid_row.delete()
        except:
            close_bid.winner = listing_row.owner
            close_bid.winprice = listing_row.price
            close_bid.save()
        try:
            if Watchlist.objects.filter(listing_id=listing_id):
                watchrow = Watchlist.objects.filter(listing_id=listing_id)
                watchrow.delete()
            else:
                pass
        except:
            pass
        try:
            comment_row = Comment.objects.filter(listing_id=listing_id)
            comment_row.delete()
        except:
            pass
        try:
            bid_row = Bid.objects.filter(listing_id=listing_id)
            bid_row.delete()
        except:
            pass
        try:
            close_bidlist=Closedbid.objects.get(listing_id=listing_id)
        except:
            close_bid.owner = listing_row.owner
            close_bid.winner = listing_row.owner
            close_bid.listing_id = listing_id
            close_bid.winprice = listing_row.price
            close_bid.save()
            close_bidlist=Closedbid.objects.get(listing_id=listing_id)
        listing_row.delete()
        try:
            w = Watchlist.objects.filter(user=request.user.username)
            watchcount = len(w)
            if len(w) == 0:
                watchcount = 0
        except:
            watchcount = 0
        return render(request,"auctions/winningItem.html",{
            "close_bid":close_bidlist,
            "title":title,
            "watchcount":watchcount
        })   

    else:
        return redirect('index')     

@login_required
def winnings(request):
    if request.user.username:
        items = []
        try:
            winningItems = Closedbid.objects.filter(winner=request.user.username)
            for w in winningItems:
                items.append(All_Listings.objects.filter(listing_id=w.listing_id))
            items = [ele for ele in reversed(items)]
        except:
            winningItems = None
            items = None
        try:
            w = Watchlist.objects.filter(user=request.user.username)
            watchcount = len(w)
            if len(w) == 0:
                watchcount = 0
        except:
            watchcount = 0
        return render(request,'auctions/winnings.html',{
            "items":items,
            "watchcount":watchcount,
            "winningItems":winningItems
        })
    else:
        return redirect('index')

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
from django.shortcuts import render, redirect
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count
from math import ceil
from django.db.models import Q

# Create your views here.
from django.shortcuts import render
from django.db.models import Q


def index(request):
    category = request.GET.get("category","")
    sort_by_price = request.GET.get("sort_by_price","")
    sort_by_arrival = request.GET.get("sort_by_arrival","")

    products = Product.objects.all()

    if category:
        products = products.filter(category=category)

    if sort_by_price == "asc":
        products = products.order_by("price")
    elif sort_by_price == "desc":
        products = products.order_by("-price")

    if sort_by_arrival == "old":
        products = products.order_by("pub_date")
    elif sort_by_arrival == "new":
        products = products.order_by("-pub_date")

    allProds = []
    catprods = products.values("category", "id")
    cats = {item["category"] for item in catprods}
    for cat in cats:
        prod = products.filter(category=cat)
        n = len(prod)
        nSlides = n // 3 + ceil((n / 3) - (n // 3))
        allProds.append([prod, range(1, nSlides), nSlides])

    categories = Product.objects.values("category").distinct()
    params = {
        "allProds": allProds,
        "categories": categories,
        "selected_category": category,
        "selected_sort_price": sort_by_price,
        "selected_sort_arrival": sort_by_arrival,
    }

    return render(request, "shop/index.html", params)


# def index(request):

#     allProds = []
#     catprods = Product.objects.values("category", "id")
#     cats = {item["category"] for item in catprods}
#     for cat in cats:
#         prod = Product.objects.filter(category=cat)
#         n = len(prod)
#         nSlides = n // 3 + ceil((n / 3) - (n // 3))
#         allProds.append([prod, range(1, nSlides), nSlides])
#     categories = Product.objects.values("category").distinct()
#     params = {"allProds": allProds, "categories": categories}

#     return render(request, "shop/index.html", params)


# def index(request):
#     category_filter = request.GET.get("category", "")
#     sort_by_price = request.GET.get("sort_by_price", "")
#     sort_by_arrival = request.GET.get("sort_by_arrival", "")

#     base_query = Product.objects.all()

#     if category_filter:
#         base_query = base_query.filter(category=category_filter)

#     if sort_by_price == "asc":
#         base_query = base_query.order_by("price")
#     elif sort_by_price == "desc":
#         base_query = base_query.order_by("-price")
#     elif sort_by_arrival == "old":
#         base_query = base_query.order_by("pub_date")
#     elif sort_by_arrival == "new":
#         base_query = base_query.order_by("-pub_date")

#     # Get categories with products after applying the filter
#     catprods = base_query.values("category").annotate(count=Count("category"))
#     cats = catprods.filter(count__gt=0).values_list("category", flat=True)
#     categories = Product.objects.values("category").distinct()
#     allProds = []

#     for cat in cats:
#         prod = base_query.filter(category=cat)
#         n = len(prod)
#         nSlides = n // 3 + ceil((n / 3) - (n // 3))
#         allProds.append([prod, range(1, nSlides), nSlides])

#     params = {"allProds": allProds, "categories": categories}
#     return render(request, "shop/index.html", params)


def about(request):
    return render(request, "shop/about.html")


def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        phone = request.POST.get("phone", "")
        desc = request.POST.get("desc", "")
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, "shop/contact.html", {"thank": thank})


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get("orderId", "")
        email = request.POST.get("email", "")
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({"text": item.update_desc, "time": item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse("{}")
        except Exception as e:
            return HttpResponse("{}")

    return render(request, "shop/tracker.html")


def productView(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, "shop/productView.html", {"product": product[0]})


# @login_required
def checkout(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            # User is not authenticated, redirect to login page
            return redirect("accounts:login")  # Replace 'login' with the actual URL
        items_json = request.POST.get("itemsJson", "")
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        address = (
            request.POST.get("address1", "") + " " + request.POST.get("address2", "")
        )
        city = request.POST.get("city", "")
        state = request.POST.get("state", "")
        zip_code = request.POST.get("zip_code", "")
        phone = request.POST.get("phone", "")
        order = Orders(
            items_json=items_json,
            name=name,
            email=email,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone,
        )
        order.save()
        update = OrderUpdate(
            order_id=order.order_id, update_desc="The order has been placed"
        )
        update.save()
        thank = True
        id = order.order_id
        return render(request, "shop/checkout.html", {"thank": thank, "id": id})
    return render(request, "shop/checkout.html")


def search(request):
    query = request.GET.get("search")
    allProds = []
    catprods = Product.objects.values("category", "id")
    cats = {item["category"] for item in catprods}

    # Check if the query is of sufficient length
    if len(query) < 4:
        params = {"msg": "Please make sure to enter a relevant search query"}
    else:
        for cat in cats:
            prod = Product.objects.filter(
                Q(category=cat)
                & (Q(product_name__icontains=query) | Q(desc__icontains=query))
            )

            if prod:
                n = len(prod)
                nSlides = n // 4 + ceil((n / 4) - (n // 4))
                allProds.append([prod, range(1, nSlides), nSlides])

        if not allProds:
            params = {"msg": "No products match your search query."}
        else:
            params = {"allProds": allProds, "msg": ""}

    return render(request, "shop/index.html", params)

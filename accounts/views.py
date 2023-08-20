from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from .forms import SignupForm
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from .tokens import account_activation_token


def login_user(request):
    if request.user.is_authenticated:
        return redirect("home:home")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("Home")
        else:
            messages.error(
                request,
                "Username Or Password is incorrect!",
                extra_tags="alert alert-warning alert-dismissible fade show",
            )
    return render(request, "accounts/login.html")


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("Home")
    return redirect("Home")


def create_user(request):
    # If loggedin->Home
    if request.user.is_authenticated:
        return redirect("Home")
    ## If register form submitted
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]

            check1 = False
            check2 = False
            if User.objects.filter(username=username).exists():
                check1 = True
                messages.error(
                    request,
                    "Username already exists!",
                    extra_tags="alert alert-warning alert-dismissible fade show",
                )

            if User.objects.filter(email=email).exists():
                check2 = True
                messages.error(
                    request,
                    "Email already registered!",
                    extra_tags="alert alert-warning alert-dismissible fade show",
                )

            if check1 or check2:
                return redirect("accounts:signup")
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                messages.success(
                    request,
                    "Successfully registered, Please check your registered mail and verify",
                    extra_tags="alert alert-success alert-dismissible fade show",
                )
      

                try:
                    email_subject = "Confirm your email"
                    email_from = settings.EMAIL_HOST_USER  # Email of sender
                    to_email = email
                    current_site = get_current_site(request)
                    # Render HTML content from a template
                    html_content = render_to_string(
                        "email_confirmation.html",
                        {
                            "username": username,
                            "domain": current_site.domain,
                            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                            "token": account_activation_token.make_token(user),
                        },
                    )

                    # Create the plaintext version of the email
                    text_content = strip_tags(html_content)

                    # Create the email object
                    email = EmailMultiAlternatives(
                        email_subject,
                        text_content,
                        email_from,
                        to=[to_email],
                    )

                    # Attach the HTML content to the email
                    email.attach_alternative(html_content, "text/html")
                    # Send email
                    email.send()
                except:
                    print("Some error occured")

                return redirect("accounts:login")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and account_activation_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect("Home")
    else:
        messages.error(
            request,
            " Activation failed, Please try again!",
            extra_tags="alert alert-warning alert-dismissible fade show",
        )
        return redirect(request, "accounts:signup")




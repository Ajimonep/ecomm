from django.shortcuts import render,redirect

from django.views.generic import View

from store.forms import SignUpForm,LoginForm

from django.core.mail import send_mail

from store.models import User,Size,BasketItem

from django.contrib import messages

from django.contrib.auth import authenticate,login

from store.models import Product

def send_otp_phone(otp):

    from twilio.rest import Client
    account_sid = 'AC83ec1f17cb61816e1408a9cea6a6e1c8'
    auth_token = "f5fb39f513f36a64695a1fc9117ff493"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    from_='+15075937854',
    body=otp,
    to='+919496591658'
)
    print(message.sid)


def send_otp_email(user):

    user.generate_otp()

    # send_otp_phone(user.otp)

    subject="verify your email"

    message=f"otp for account verification is {user.otp}"

    from_email="ajimon031@gmail.com"

    to_email=[user.email]

    send_mail(subject,message,from_email,to_email )


class SignUpView(View):

    template_name="register.html"

    form_class=SignUpForm

    def get(self,request,*args,**kwargs):

        form_instance=self.form_class()

        return render(request,self.template_name,{"form":form_instance})

    def post(self,request,*args,**kwargs):

        form_data=request.POST 

        form_instance=self.form_class(form_data)

        if form_instance.is_valid():

            user_object=form_instance.save(commit=False)

            user_object.is_active=False

            user_object.save()

            send_otp_email(user_object)

            return redirect("verify-email")

        return render(request,self.template_name,{"form":form_instance})


class VerifyEmailView(View):

    template_name="verify_email.html"

    def get(self,request,*args,**kwargs):

        return render(request,self.template_name)

    def post(self,request,*args,**kwargs):

        otp=request.POST.get("otp")

        try:

            user_object=User.objects.get(otp=otp)

            user_object.is_active=True

            user_object.is_verified=True

            user_object.otp=None

            user_object.save()

            return redirect("signin")

        except:

            messages.error(request,"invalid otp")

            return render(request,self.template_name)

class SignInView(View):

    template_name="signin.html"

    form_class=LoginForm

    def get(self,request,*args,**kwargs):

        form_instance=self.form_class()

        return render(request,self.template_name,{"form":form_instance})

    def post(self,request,*args,**kwargs):

        form_data=request.POST 

        form_instance=self.form_class(form_data)

        if form_instance.is_valid():

            uname=form_instance.cleaned_data.get("username")

            pwd=form_instance.cleaned_data.get("password")

            user_object=authenticate(request,username=uname,password=pwd)

            if user_object:

                login(request,user_object)

                return redirect("product-list")

        return render(request,self.template_name,{"form":form_instance})

class ProductListView(View):

    template_name="index.html"

    def get(self,request,*args,**kwargs):

        qs=Product.objects.all()

        return render(request,self.template_name,{"data":qs})


class productDetailView(View):

    template_name="product_detail.html"

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        qs=Product.objects.get(id=id)

        return render(request,self.template_name,{"product":qs})

class AddToCartView(View):

    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        size=request.POST.get("size")

        quantity=request.POST.get("quantity")

        product_object=Product.objects.get(id=id)

        size_object=Size.objects.get(name=size)

        basket_object=request.user.cart

        BasketItem.objects.create(
            product_object=product_object,
            quantity=quantity,
            size_object=size_object,
            basket_object=basket_object
        )

        print("item has been added to cart")

        return redirect("cart-summary")


class CartSummaryView(View):

    template_name="cart_summary.html"

    def get(self,request,*args,**kwargs):

        qs=BasketItem.objects.filter(basket_object=request.user.cart,is_order_placed=False)

        basket_item_count=qs.count()

        basket_total=sum([bi.item_total for bi in qs])


        return render(request,self.template_name,{"basket_items":qs,"basket_total":basket_total,"basket_item_count":basket_item_count})
    
class ItemDeleteView(View):


    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")

        BasketItem.objects.get(id=id).delete()

        return redirect("cart-summary")






    

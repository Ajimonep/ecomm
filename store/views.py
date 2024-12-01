from django.shortcuts import render,redirect

from django.views.generic import View

from store.forms import SignUpForm,LoginForm,OrderForm

from django.core.mail import send_mail

from store.models import User,Size,BasketItem,OrderItem

from django.contrib import messages

from django.contrib.auth import authenticate,login

from store.models import Product

from django.core.paginator import Paginator

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

        paginator=Paginator(qs,4)

        page_number=request.GET.get("page")

        page_obj=paginator.get_page(page_number)

        return render(request,self.template_name,{"page_obj":page_obj})

    """
    current page number - ?page={{page_obj.number}}

    next page number - ?page={{page_obj.next_page_number}}

    previous page number - ?page={{page_obj.previous_page_number}}

    last page number - ?page={{page_obj.paginator.num_pages}}

    
    """


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

        
class PlaceOrderView(View):

    form_class=OrderForm

    template_name="order.html"

    def get(self,request,*args,**kwargs):

        form_instance=self.form_class()

        qs=request.user.cart.cart_item.filter(is_order_placed=False)

        return render(request,self.template_name,{"form":form_instance,"items":qs})


    def post(self,request,*args,**kwargs):

        form_data=request.POST 

        form_instance=self.form_class(form_data)

        if form_instance.is_valid():

            form_instance.instance.customer=request.user

            order_instance=form_instance.save()

            basket_item=request.user.cart.cart_item.filter(is_order_placed=False)

            for bi in basket_item:

                OrderItem.objects.create(
                    order_object=order_instance,
                    product_object=bi.product_object,
                    quantity=bi.quantity,
                    size_object=bi.size_object,
                    price=bi.product_object.price
                )

                bi.is_order_placed=True

                bi.save()

        return redirect("product-list")





class OrderSummaryView(View):

    template_name="order_summary.html"

    def get(self,request,*args,**kwargs):

        qs=request.user.orders.all()

        return render(request,self.template_name,{"orders":qs})
    

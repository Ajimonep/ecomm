from django.shortcuts import render,redirect

from django.views.generic import View

from store.forms import SignUpForm

from django.core.mail import send_mail

from store.models import User

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

    send_otp_phone(user.otp)

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

        user_object=User.objects.get(otp=otp)

        user_object.is_active=True

        user_object.is_verified=True

        user_object.otp=None

        user_object.save()


        return redirect("signup")


    

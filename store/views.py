from django.shortcuts import render,redirect

from django.views.generic import View

from store.forms import SignUpForm

from django.core.mail import send_mail

def send_otp_email(user):

    user.generate_otp()

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

        


class VerifyEmailView(View):

    template_name="verify_email.html"

    def get(self,request,*args,**kwargs):

        return render(request,self.template_name)
    

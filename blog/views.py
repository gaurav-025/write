from django.shortcuts import render, get_object_or_404,redirect
from .models import Post,Tag
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from .forms import CustomRegistrationForm,CustomLoginForm,CustomPasswordResetForm,PostForm,CommentForm
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import markdown2
import json
from django.core.paginator import Paginator
import os


def home(request):
    posts=Post.objects.all().order_by('-created_at')
    paginator=Paginator(posts,12)

    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    return render(request,'blog/post_list.html',{'page_obj':page_obj})

def post_detail(request,slug):
    post=get_object_or_404(Post,slug=slug)
    post.content_html=markdown2.markdown(post.content,
        extras=[
            "fenced-code-blocks",
            "tables",
            "code-friendly",
            "strike",
            "break-on-newline",
            "target-blank-links",
            "header-ids",
        ])
    comments=post.comments.order_by('-created_at')
    comment_form=CommentForm()

    if request.method=='POST':
        if not request.user.is_authenticated:
            return redirect('custom_login')

        comment_form=CommentForm(request.POST)
        if comment_form.is_valid():
            comment=comment_form.save(commit=False)
            comment.post=post
            comment.user=request.user
            comment.save()
            return redirect('post_detail',slug=slug)
        

    return render(request,'blog/post_detail.html',{
        'post':post,
        'comments':comments,
        'comment_form':comment_form,
        })

def edit_post(request,pk):
    post=get_object_or_404(Post,pk=pk)
    if post.author!=request.user:
        raise PermissionDenied("You do not have permission to edit this post.")
    if request.method=='POST':
        form=PostForm(request.POST,instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form=PostForm(instance=post)

    return render(request,'blog/edit_post.html',{'form':form,'post':post})


def custom_register(request):
    if request.method=='POST':
        form=CustomRegistrationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            # password=form.cleaned_data['password']
            # password_confirm=form.cleaned_data['password_confirm']
            user.is_active=False
            user.save()

            token=default_token_generator.make_token(user)
            uid=urlsafe_base64_encode(force_bytes(user.pk))
            domain=get_current_site(request).domain
            activation_link=reverse('verify_email',kwargs={'uidb64':uid,'token':token})
            verify_url=f'http://{domain}{activation_link}'

            subject='Verify your email for Write'
            message=f'Hi {user.username},\n\nPlease verify your email by clicking the link:\n{verify_url}'

            print(subject)
            print(message)
            print(email)

            send_mail(subject,message,settings.DEFAULT_FROM_EMAIL,[email])

            messages.success(request,"registration successfull. Check your email to verify your account.")

            request.session['email_verification_pending']=True

            return redirect('email_verification_notice')
    else:
        form=CustomRegistrationForm()
    return render(request,'registration/register.html',{'form':form})

def custom_login(request):
    if request.method=='POST':
        form=CustomLoginForm(request.POST)
        if form.is_valid():
            # user=form.get_user()
            # login(request,user)
            username_or_email=form.cleaned_data['username']
            password=form.cleaned_data['password']
            user=authenticate(request,username=username_or_email,password=password)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in successfully!")
                return redirect('home')
            # return redirect('home')
            else:
                form.add_error(None,"Invalid Credentials")
    else:
        form=CustomLoginForm()
    return render(request,'registration/login.html',{'form':form})

def custom_logout(request):
    logout(request)
    messages.success(request,"Logged out successfully!")
    return redirect('home')

def verify_email(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user=None
    
    if user and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,"Your email is now verified. You can now log in.")
        return redirect('custom_login')
    else:
        messages.error(request,'Invalid or expired verification link.')
        return redirect('custom_register')

def email_verification_notice(request):
    if request.session.get('email_verification_pending'):
        del request.session['email_verification_pending']
        return render(request,'registration/email_verification_notice.html')
    else:
        return HttpResponseForbidden("You are not authorized to access this page.")

def password_reset_request(request):
    if request.method=='POST':
        form=CustomPasswordResetForm(request.POST)
        if form.is_valid():    
            email=form.cleaned_data['email']
            # print(email)
            try:
                # print(email)
                user=User.objects.get(email=email)
                
                token=default_token_generator.make_token(user)
                uid=urlsafe_base64_encode(force_bytes(user.pk))
                    # print(token)
                    # print(uid)
                domain=get_current_site(request).domain
                activation_link=reverse('custom_password_reset_confirm',kwargs={'uidb64':uid,'token':token})
                reset_link=f'http://{domain}{activation_link}'
                    # print(reset_link)
                    # message=render_to_string("registration/password_reset_email.html",{
                    #     'reset_link':reset_link,
                    #     'user':user
                    # })
                message=f'Hello {user.username},\nClick the below link to reset your password:\n {reset_link}'
                    # print(message)
            # print(os.getenv("EMAIL_HOST_USER"))
                send_mail(
                    subject="Password Reset Requested",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                        # html_message=message
                )

                messages.success(request,"If the email exists, a reset link has been sent.")
                return redirect('custom_login')
            except User.DoesNotExist:
                form.add_error('email',"No user is associated with this email.")
    else:
        form=CustomPasswordResetForm()
        
    return render(request,'registration/password_reset_request.html',{'form':form})

def custom_password_reset_confirm(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        user=User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError,TypeError):
        user=None
    
    if user is not None and default_token_generator.check_token(user,token):
        if request.method=="POST":
            new_password=request.POST.get("password")
            confirm_password=request.POST.get("confirm_password")
            if new_password==confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request,"Password successfully reset.")
                return redirect("custom_login")
            else:
                messages.error(request,"Passwords do not match.")
        return render(request,"registration/custom_password_reset_confirm.html",{'validlink':True})
    messages.error(request,"The reset link is invalid or expired.")
    return render(request,"registration/custom_password_reset_confirm.html",{'validlink':False})

@login_required
def create_post(request):
    if request.method=='POST':
        form=PostForm(request.POST)
        if form.is_valid():
            post=form.save(commit=False)
            visibility=request.POST.get('visibility')
            if visibility=='anonymous':
                anonymous_user, created = User.objects.get_or_create(username='Anonymous')
                post.author = anonymous_user
            else:
                post.author=request.user
            
            post.content_html=markdown2.markdown(
                post.content,
                extras=["fenced-code-blocks", "tables", "code-friendly", "toc", "strike", "target-blank-links"],
        
            )


            post.save()

            raw_tags=form.cleaned_data['tags']
            try:
                tag_list=json.loads(raw_tags)
                tag_objs=[]
                for tag_dict in tag_list:
                    tag_name=tag_dict.get('value')
                    if tag_name:
                        tag_obj,_=Tag.objects.get_or_create(name=tag_name)
                        tag_objs.append(tag_obj)
                post.tags.set(tag_objs)
            except json.JSONDecodeError:
                post.tags.clear()
            return redirect('home')
    else:
        form=PostForm()
    return render(request,'blog/create_post.html',{'form':form})
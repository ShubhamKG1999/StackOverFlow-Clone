# views.py
import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import StackOverFlowUser, Follow, Question

def index(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return render(request, 'index.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect('feed')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
            else:
                # Hash the password
                hashed_password = make_password(password)
                # Create a new user
                user = User(username=username, email=email, password=hashed_password)
                user.save()

                # Create a new entry in StackOverFlowUser model
                stackoverflow_user = StackOverFlowUser(user=user)
                stackoverflow_user.save()

                return redirect('login')
        else:
            messages.error(request, 'Password and Confirm Password do not match.')
    
    return render(request, 'signup.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('feed')
    return render(request, 'login.html')

@login_required(login_url='index')
def feed(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    # Get the questions of the following users
    questions = Question.objects.filter(user__in=following_users).order_by('-created_at')
    context = {'questions': questions}
    return render(request, 'feed.html', context)

@login_required(login_url='index')
def profile(request):
    username = request.GET.get('username')  # Get the username parameter from the URL
    if username:
        # If username parameter is present, retrieve the user and pass to profileother.html template
        try:
            user = User.objects.get(username=username)
            context = {'user': user}
            return render(request, 'profileother.html', context)
        except User.DoesNotExist:
            pass  # Handle the case where the user does not exist
    return render(request, 'profileself.html')

@login_required(login_url='index')
def logout_view(request):
    logout(request)
    return redirect('index')

def users(request):
    users = User.objects.all()  # Fetch all Django users
    users_with_karma_and_follow = []
    logged_in_user = request.user  # Get the currently logged-in user
    for user in users:
        if not user.username == logged_in_user.username:
            stackoverflow_user = StackOverFlowUser.objects.get(user=user)  # Retrieve StackOverflowUser based on Django user
            karma = stackoverflow_user.karma  # Retrieve karma value of the user
            follow = Follow.objects.filter(follower=logged_in_user, following=user).first()  # Check if logged-in user is following this user
            users_with_karma_and_follow.append({'user': user, 'karma': karma, 'is_following': follow is not None})  # Add user, karma, and follow status to a list of dictionaries

    return render(request, 'users.html', {'users': users_with_karma_and_follow})

def follow(request, username):
    user_to_follow = User.objects.get(username=username)  # Get the user to follow based on the username
    Follow.objects.get_or_create(follower=request.user, following=user_to_follow)  # Create a Follow object or retrieve existing object if already following
    return redirect('users')  # Redirect back to the users page

def unfollow(request, username):
    user_to_unfollow = User.objects.get(username=username)  # Get the user to unfollow based on the username
    follow = Follow.objects.filter(follower=request.user, following=user_to_unfollow).first()  # Retrieve the Follow object for the user to unfollow
    if follow:
        follow.delete()  # Delete the Follow object to unfollow
    return redirect('users')

def following(request):
    # Retrieve the Follow objects for the logged-in user
    following_users = Follow.objects.filter(follower=request.user)
    context = {'following_users': following_users}
    return render(request, 'following.html', context)

def followers(request):
    # Retrieve the Follow objects where the logged-in user is being followed
    followers = Follow.objects.filter(following=request.user)
    context = {'followers': followers}
    return render(request, 'followers.html', context)

def ask_question(request):
    if request.method == 'POST':
        # Get form data from request POST
        title = request.POST['title']
        description = request.POST['description']
        user = request.user

        # Create a new Question object
        question = Question(title=title, description=description, user=user)
        question.save()

        # Redirect to the feed page or any other page
        return redirect('feed')

    return render(request, 'ask_question.html')

@login_required
def my_questions(request):
    # Retrieve questions asked by the currently logged-in user
    questions = Question.objects.filter(user=request.user)
    context = {'my_questions': questions}
    return render(request, 'my_questions.html', context)

def question(request):
    question_id = request.GET['question_id']
    question = get_object_or_404(Question, id=question_id)
    # Check if the logged-in user is the owner of the question
    if question.user == request.user:
        # Render the questionself.html template with the question object as context
        context = {'question': question}
        return render(request, 'questionself.html', context)
    else:
        # Render the question.html template with the question object as context
        context = {'question': question}
        return render(request, 'question.html', context)

def delete_question(request, question_id):
    # Retrieve the question object based on the question_id parameter
    question = get_object_or_404(Question, id=question_id)

    # Check if the logged-in user is the owner of the question
    if question.user == request.user:
        # Delete the question
        question.delete()
        messages.success(request, 'Question deleted successfully.')
        # Redirect back to the feed page
        return redirect('feed')
    else:
        # Redirect to an error page or show an error message
        messages.error(request, 'You do not have permission to delete this question.')
        # Redirect back to the question details page
        return redirect('question', question_id=question.id)
    
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        # Get the updated data from the form
        title = request.POST['title']
        description = request.POST['description']

        # Update the question data in the database
        question.title = title
        question.description = description
        question.save()

        # Render the question.html template with the updated question object as context
        context = {'question': question}
        return render(request, 'questionself.html', context)

    # Render the edit.html template with the question object as context
    context = {'question': question}
    return render(request, 'edit.html', context)

def vote_question(request, question_id):
    # Retrieve the question object
    question = Question.objects.get(id=question_id)

    if request.method == 'POST':
        # Retrieve the selected vote options and initial points value from the form data
        votes = request.POST.getlist('vote')
        initial_points = int(request.POST.get('initial_points'))

        # Check if user has already voted for increase or decrease
        has_voted_increase = 'increase' in votes
        has_voted_decrease = 'decrease' in votes

        # Update the question points based on the selected vote options
        for vote in votes:
            if vote == 'increase':
                if has_voted_decrease:
                    question.points += 2
                else:
                    question.points += 1
            elif vote == 'decrease':
                if has_voted_increase:
                    question.points -= 2
                else:
                    question.points -= 1

        # If no vote option is selected, reset points to initial value
        if not votes:
            question.points = initial_points

        # Save the updated question object
        question.save()

        # Return the updated question points as a JSON response
        response_data = {'question_points': question.points}
        return JsonResponse(response_data)

    # Render the question details page
    context = {'question': question}
    return render(request, 'question.html', context)
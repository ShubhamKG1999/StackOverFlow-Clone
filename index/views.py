# views.py
import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import StackOverFlowUser, Follow, Question, QuestionVote, QuestionComment, Answer, AnswerVote

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
    # Get the questions of the following users, annotate with count of answers
    questions = Question.objects.filter(user__in=following_users).annotate(num_answers=Count('answer')).order_by('-created_at')
    context = {'questions': questions}
    return render(request, 'feed.html', context)

@login_required(login_url='index')
def new(request):
    questions = Question.objects.annotate(num_answers=Count('answer')).order_by('-created_at')
    context = {'questions': questions}
    return render(request, 'feed.html', context)

@login_required(login_url='index')
def top(request):
    questions = Question.objects.annotate(num_answers=Count('answer')).order_by('-points')
    context = {'questions': questions}
    return render(request, 'feed.html', context)

@login_required(login_url='index')
def profile(request):
    username = request.GET.get('username')  # Get the username parameter from the URL
    if username:
        # If username parameter is present, retrieve the user and pass to profileother.html template
        try:
            user = User.objects.get(username=username)
            stackoverflow_user = StackOverFlowUser.objects.get(user=user)
            questions_asked = Question.objects.filter(user=user).count()
            answers_given = Answer.objects.filter(user=user).count()
            question_votes = QuestionVote.objects.filter(user=user).count()
            answer_votes = AnswerVote.objects.filter(user=user).count()
            total_votes = question_votes + answer_votes
            context = {
                'user': user,
                'stackoverflow_user': stackoverflow_user,
                'questions_asked': questions_asked,
                'answers_given': answers_given,
                'total_votes': total_votes
            }
            return render(request, 'profileother.html', context)
        except User.DoesNotExist:
            pass  # Handle the case where the user does not exist
    else:
        user = request.user
        stackoverflow_user = StackOverFlowUser.objects.get(user=user)
        questions_asked = Question.objects.filter(user=user).count()
        answers_given = Answer.objects.filter(user=user).count()
        question_votes = QuestionVote.objects.filter(user=user).count()
        answer_votes = AnswerVote.objects.filter(user=user).count()
        total_votes = question_votes + answer_votes
        context = {
            'user': user,
            'stackoverflow_user': stackoverflow_user,
            'questions_asked': questions_asked,
            'answers_given': answers_given,
            'total_votes': total_votes
        }
        return render(request, 'profileself.html', context)

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

    return render(request, 'users.html', {'users': users_with_karma_and_follow, 'logged_in_username': logged_in_user.username})

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

        # Redirect to the question details view with the created question's ID in the query parameters
        return redirect('question_details', question_id=question.id)

    return render(request, 'ask_question.html')

def question_details(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.filter(question=question)
    user_answered = Answer.objects.filter(user=request.user, question=question).exists()

    if question.user == request.user:
        context = {'question': question, 'answers': answers, 'user_answered': user_answered}
        return render(request, 'questionself.html', context)
    else:
        context = {'question': question, 'answers': answers, 'user_answered': user_answered}
        return render(request, 'question.html', context)

@login_required
def my_questions(request):
    # Retrieve questions asked by the currently logged-in user
    questions = Question.objects.filter(user=request.user).annotate(num_answers=Count('answer')).order_by('-created_at')
    context = {'my_questions': questions}
    return render(request, 'my_questions.html', context)

def question(request):
    question_id = request.GET['question_id']
    question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.filter(question=question)
    comments = QuestionComment.objects.filter(question=question) # Get all comments related to the question

    # Check if the logged-in user has already answered the question
    user_answered = Answer.objects.filter(user=request.user, question=question).exists()

    # Render the appropriate template based on whether the user has answered the question or not
    if question.user == request.user:
        # Render the questionself.html template with the question, answers, and comments as context
        context = {'question': question, 'answers': answers, 'comments': comments, 'user_answered': user_answered}
        return render(request, 'questionself.html', context)
    else:
        # Render the question.html template with the question, answers, and comments as context
        context = {'question': question, 'answers': answers, 'comments': comments, 'user_answered': user_answered}
        return render(request, 'question.html', context)

def delete_question(request, question_id):
    # Retrieve the question object based on the question_id parameter
    question = get_object_or_404(Question, id=question_id)

    # Check if the logged-in user is the owner of the question
        # Delete the question
    question.delete()
    messages.success(request, 'Question deleted successfully.')
        # Redirect back to the feed page
    return redirect('feed')

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
        initial_points = int(request.POST.get('initial_points', 0))

        # Update the question points based on the selected vote options
        for vote in votes:
            if vote == 'increase':
                # Check if user has already voted and vote_type is 1, then increase by 2
                if QuestionVote.objects.filter(user=request.user, question=question, vote_type=-1).exists():
                    question.points += 2
                else:
                    question.points += 1
            elif vote == 'decrease':
                # Check if user has already voted and vote_type is -1, then decrease by 2
                if QuestionVote.objects.filter(user=request.user, question=question, vote_type=1).exists():
                    question.points -= 2
                else:
                    question.points -= 1

        # If no vote option is selected, reset points to initial value
        if not votes:
            if QuestionVote.objects.filter(user=request.user, question=question, vote_type=-1).exists():
                question.points += 1
            elif QuestionVote.objects.filter(user=request.user, question=question, vote_type=1).exists():
                question.points -= 1
            else:
                question.points = initial_points

        # Save the updated question object
        question.save()

        # Retrieve the user object from the request
        user = request.user

        # Update or create a QuestionVote object for the user and question
        question_vote, created = QuestionVote.objects.update_or_create(
            user=user,
            question=question,
            defaults={'vote_type': 1 if 'increase' in votes else -1 if 'decrease' in votes else 0}
        )

        question_votes = QuestionVote.objects.all()

        # Iterate through the objects and print the vote_type field value

        # Return the updated question points as a JSON response
        response_data = {'question_points': question.points}
        return JsonResponse(response_data)

    # Render the question details page
    context = {'question': question}
    return render(request, 'question.html', context)

def vote_answer(request, answer_id):
    # Retrieve the answer object
    answer = Answer.objects.get(id=answer_id)

    if request.method == 'POST':
        # Retrieve the selected vote options and initial points value from the form data
        votes = request.POST.getlist('vote')
        initial_points = int(request.POST.get('initial_points', 0))

        # Update the answer points based on the selected vote options
        for vote in votes:
            if vote == 'increase':
                # Check if user has already voted and vote_type is 1, then increase by 2
                if AnswerVote.objects.filter(user=request.user, answer=answer, vote_type=-1).exists():
                    answer.points += 2
                else:
                    answer.points += 1
            elif vote == 'decrease':
                # Check if user has already voted and vote_type is -1, then decrease by 2
                if AnswerVote.objects.filter(user=request.user, answer=answer, vote_type=1).exists():
                    answer.points -= 2
                else:
                    answer.points -= 1

        # If no vote option is selected, reset points to initial value
        if not votes:
            if AnswerVote.objects.filter(user=request.user, answer=answer, vote_type=-1).exists():
                answer.points += 1
            elif AnswerVote.objects.filter(user=request.user, answer=answer, vote_type=1).exists():
                answer.points -= 1
            else:
                answer.points = initial_points

        # Save the updated answer object
        answer.save()

        # Retrieve the user object from the request
        user = request.user

        # Update or create an AnswerVote object for the user and answer
        answer_vote, created = AnswerVote.objects.update_or_create(
            user=user,
            answer=answer,
            defaults={'vote_type': 1 if 'increase' in votes else -1 if 'decrease' in votes else 0}
        )

        answer_votes = AnswerVote.objects.all()

        # Iterate through the objects and print the vote_type field value

        # Return the updated answer points as a JSON response
        response_data = {'answer_points': answer.points}
        return JsonResponse(response_data)

    # Render the answer details page
    context = {'answer': answer}
    return render(request, 'answer.html', context)

def get_user_vote(request):
    if request.method == 'GET':
        question_id = request.GET.get('question_id')  # Get question ID from request parameters
        question = get_object_or_404(Question, id=question_id)  # Fetch the question object
        
        # Fetch the vote object for the logged in user and the question
        try:
            vote = QuestionVote.objects.get(user=request.user, question=question)
            vote_type = vote.vote_type  # Get the vote type (1 for increase, -1 for decrease)
        except QuestionVote.DoesNotExist:
            vote_type = 0  # If no vote exists, set vote type to 0 (no vote)

        data = {
            'vote_type': vote_type  # Return the vote type in response data
        }
        return JsonResponse(data)
    
def search(request):
    if request.method == 'GET':
        query = request.GET.get('query') # Get the value of 'query' from the form submission
        # Perform search logic based on the query, e.g., querying the database
        # with the query and retrieving relevant results
        # You can customize this logic based on your application's requirements

        # Assuming you have a 'Question' model in your Django application
        questions = Question.objects.filter(title__icontains=query).annotate(num_answers=Count('answer')) # Example search logic

        # Render the search results in a template
        return render(request, 'search_results.html', {'questions': questions, 'query': query})
    else:
        # Render the search page if the form is not submitted with GET method
        return render(request, 'feed.html')


def base(request):
    following_users = Follow.objects.filter(follower=request.user)
    followers = Follow.objects.filter(following=request.user)
    
    context = {'following_users': following_users, 'followers': followers}
    
    return render(request, 'base.html', context)

def add_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        answer_text = request.POST['answer_text']
        user = request.user
        answer = Answer(user=user, question=question, answer_text=answer_text)
        answer.save()

    comments = QuestionComment.objects.filter(question=question)
    answers = Answer.objects.filter(question=question)
    
    # Check if the question belongs to the logged-in user
    if question.user == request.user:
        context = {'question': question, 'answers': answers, 'comments': comments, 'user_answered': True}
        return render(request, 'questionself.html', context)
    else:
        context = {'question': question, 'answers': answers, 'comments': comments, 'user_answered': True}
        return render(request, 'question.html', context)

def add_comment(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        comment_content = request.POST['comment_content']
        user = request.user
        comment = QuestionComment(user=user, question=question, comment_text=comment_content)
        comment.save()

    user_answered = Answer.objects.filter(user=request.user, question=question).exists()
    comments = QuestionComment.objects.filter(question=question)
    answers = Answer.objects.filter(question=question)
    
    # Check if the question belongs to the logged-in user
    if question.user == request.user:
        context = {'question': question, 'answers': answers, 'comments': comments, 'user_answered': user_answered}
        return render(request, 'questionself.html', context)
    else:
        context = {'question': question, 'answers': answers, 'comments': comments, 'user_answered': user_answered}
        return render(request, 'question.html', context)

def delete_comment(request, comment_id):
    comment = get_object_or_404(QuestionComment, id=comment_id)
    question = comment.question

    if request.method == 'POST' and request.user.is_authenticated and comment.user == request.user:
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, 'Failed to delete comment.')

    comments = QuestionComment.objects.filter(question=question) # Get all comments related to the question
    answers = Answer.objects.filter(question=question) # Get all answers related to the question
    user_answered = Answer.objects.filter(user=request.user, question=question).exists()
    context = {'question': question, 'answers': answers, 'comments': comments, 'user_answered': user_answered}
    if question.user == request.user:
        return render(request, 'questionself.html', context)
    return render(request, 'question.html', context)

@login_required
def edit_profile(request):
    user = request.user
    stackoverflowuser, created = StackOverFlowUser.objects.get_or_create(user=user)

    if request.method == 'POST':
        about = request.POST['about']
        link = request.POST['link']
        profile_pic = request.FILES.get('profile_pic')
        
        # Update the stackoverflowuser fields
        stackoverflowuser.about = about
        stackoverflowuser.link = link
        if profile_pic:
            stackoverflowuser.profile_pic = profile_pic
        
        stackoverflowuser.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')  # Redirect to profile page
    else:
        initial_data = {
            'about': stackoverflowuser.about,
            'link': stackoverflowuser.link
        }
        form = None

    return render(request, 'edit_profile.html', {'form': form, 'initial_data': initial_data})

def deleteprofile(request):
    if request.method == 'GET':
        username = request.GET.get('username')  # Retrieve the 'username' parameter from the query string
        try:
            # Delete the User object
            User.objects.get(username=username).delete()
            messages.success(request, 'Your account has been deleted successfully.')
        except User.DoesNotExist:
            messages.error(request, 'Failed to delete account. Please try again.')
        return redirect('users')  # Redirect to the home page or any other page as needed
    else:
        # Redirect to home page with an error message if the request method is not GET
        messages.error(request, 'Failed to delete account. Please try again.')
        return redirect('home')
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('feed/', views.feed, name='feed'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.users, name='users'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
    path('following/', views.following, name='following'),
    path('followers/', views.followers, name='followers'),
    path('ask_question/', views.ask_question, name='ask_question'),
    path('my_questions/', views.my_questions, name='my_questions'),
    path('question/', views.question, name='question'),
    path('delete/<int:question_id>/', views.delete_question, name='delete_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/vote/', views.vote_question, name='vote_question'),
    path('get_user_vote/', views.get_user_vote, name='get_user_vote'),
    path('search/', views.search, name='search'),
    path('base/', views.base, name='base')
]
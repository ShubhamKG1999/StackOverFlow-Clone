from django.contrib import admin
from .models import StackOverFlowUser, Follow, Question, QuestionVote

# Register your models here.
admin.site.register(StackOverFlowUser)
admin.site.register(Follow)
admin.site.register(Question)
admin.site.register(QuestionVote)
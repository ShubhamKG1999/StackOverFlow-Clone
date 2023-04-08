from django.contrib import admin
from .models import StackOverFlowUser, Follow, Question, QuestionVote, QuestionComment, Answer

# Register your models here.
admin.site.register(StackOverFlowUser)
admin.site.register(Follow)
admin.site.register(Question)
admin.site.register(QuestionVote)
admin.site.register(QuestionComment)
admin.site.register(Answer)
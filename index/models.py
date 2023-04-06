from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class StackOverFlowUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    karma = models.IntegerField(default=0)
    questions_asked = models.IntegerField(default=0)
    questions_answered = models.IntegerField(default=0)
    join_date = models.DateField(default=timezone.now)  # Update default to timezone.now
    about = models.CharField(max_length=255, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Set join_date explicitly when saving the model instance
        if not self.join_date:
            self.join_date = timezone.now()
        super(StackOverFlowUser, self).save(*args, **kwargs)


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='follower', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)

class QuestionVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    vote_type = models.IntegerField(choices=((1, 'Upvote'), (-1, 'Downvote'), (0, 'No Vote')), default=0)
    created_at = models.DateTimeField(default=timezone.now)
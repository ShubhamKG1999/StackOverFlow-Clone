from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from PIL import Image

class StackOverFlowUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    karma = models.IntegerField(default=0)
    questions_asked = models.IntegerField(default=0)
    questions_answered = models.IntegerField(default=0)
    join_date = models.DateField(default=timezone.now)
    about = models.CharField(max_length=255, blank=True, null=True, default='')  # Set default value as empty string
    link = models.CharField(max_length=255, blank=True, null=True, default='')
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg', blank=True, null=True)  # Set default value as empty string
    
    def save(self, *args, **kwargs):
        if not self.join_date:
            self.join_date = timezone.now()
        super(StackOverFlowUser, self).save(*args, **kwargs)


        if self.profile_pic:
            img = Image.open(self.profile_pic.path)

            # Resize the profile picture if needed
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_pic.path)


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

class QuestionComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    comment_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)
    helpful = models.BooleanField(default=False)

class AnswerVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    vote_type = models.IntegerField(choices=((1, 'Upvote'), (-1, 'Downvote'), (0, 'No Vote')), default=0)
    created_at = models.DateTimeField(default=timezone.now)

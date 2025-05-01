from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Image(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=2000)
    source_url = models.URLField(max_length=2000)
    thumbnail_url = models.URLField(max_length=2000)
    is_transparent = models.BooleanField(default=False)
    copyright_status = models.CharField(max_length=50, choices=[
        ('free', 'Free to use'),
        ('commercial', 'Free for commercial use'),
        ('noncommercial', 'Free for noncommercial use'),
        ('modification', 'Free to modify'),
        ('unknown', 'Unknown')
    ], default='unknown')
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)  # in bytes
    file_type = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def likes_count(self):
        return self.like_set.count()
    
    @property
    def comments_count(self):
        return self.comment_set.count()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'image')
    
    def __str__(self):
        return f"{self.user.username} likes {self.image.title}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} on {self.image.title}: {self.text[:30]}"

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    query = models.CharField(max_length=255)
    filters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.query} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

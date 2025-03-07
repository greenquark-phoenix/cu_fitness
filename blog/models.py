from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """文章分类"""
    name = models.CharField(max_length=100, unique=True)  # 分类名称

    def __str__(self):
        return self.name

class Tag(models.Model):
    """文章标签"""
    name = models.CharField(max_length=50, unique=True)  # 标签名称

    def __str__(self):
        return self.name

class Post(models.Model):
    """博客文章"""
    title = models.CharField(max_length=200)  # 文章标题
    content = models.TextField()  # 文章内容
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 关联用户
    created_at = models.DateTimeField(default=timezone.now)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # 文章分类
    tags = models.ManyToManyField(Tag, blank=True)  # 多对多关联标签

    def __str__(self):
        return self.title

class Comment(models.Model):
    """评论"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # 关联文章
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 关联用户
    content = models.TextField()  # 评论内容
    created_at = models.DateTimeField(auto_now_add=True)  # 评论时间

    def __str__(self):
        return f"{self.user.username} - {self.post.title}"


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Post, Comment


@login_required
def blog_list(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')

        if title.strip() and content.strip():
            post = Post.objects.create(
                title=title,
                content=content,
                author=request.user
            )
            return JsonResponse({
                "success": True,
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "author": post.author.username,
                "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
            })

        return JsonResponse({"success": False, "message": "Title and content cannot be empty."}, status=400)

    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})


def blog_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/blog_detail.html', {'post': post})


@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("content")

        if content.strip():
            comment = Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )
            return JsonResponse({
                "success": True,
                "username": comment.user.username,
                "content": comment.content,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
            })
    return JsonResponse({"success": False}, status=400)


@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user in comment.liked_by.all():
        comment.liked_by.remove(request.user)
        comment.likes -= 1
        liked = False
    else:
        comment.liked_by.add(request.user)
        comment.likes += 1
        liked = True

    comment.save()

    return JsonResponse({"success": True, "likes": comment.likes, "liked": liked})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return JsonResponse({"success": True})

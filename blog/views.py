from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post, Comment, Category

@login_required
def blog_list(request):
    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if title and content:
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

    query = request.GET.get('q', '').strip()
    posts = Post.objects.all()

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    posts = posts.order_by('-created_at')
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/blog_list.html', {
        'posts': page_obj,
        'query': query,
    })

def blog_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/blog_detail.html', {'post': post})

@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("content", "").strip()
        parent_id = request.POST.get("parent_id")

        if content:
            parent = None
            if parent_id:
                try:
                    parent = Comment.objects.get(id=parent_id, post=post)
                except Comment.DoesNotExist:
                    return JsonResponse({"success": False, "message": "Parent comment not found."}, status=404)

            comment = Comment.objects.create(
                post=post,
                user=request.user,
                content=content,
                parent=parent
            )

            return JsonResponse({
                "success": True,
                "comment_id": comment.id,
                "username": comment.user.username,
                "content": comment.content,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
                "parent_id": parent.id if parent else None
            })

    return JsonResponse({"success": False, "message": "Comment content cannot be empty."}, status=400)

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
    return JsonResponse({
        "success": True,
        "likes": comment.likes,
        "liked": liked
    })

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user:
        return JsonResponse({"success": False, "message": "You are not authorized to delete this comment."}, status=403)

    comment.delete()
    return JsonResponse({"success": True})

@login_required
def delete_post(request, post_id):
    if request.method == "DELETE":
        post = get_object_or_404(Post, id=post_id)

        if post.author != request.user:
            return JsonResponse({"success": False, "message": "You are not authorized to delete this post."}, status=403)

        post.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

from rest_framework import viewsets

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model

from blog.models import Post
from blog.serializers import PostSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from blog.permissions import IsOwnerOrReadOnly
from .forms import PostForm


class BlogImage(viewsets.ModelViewSet):
    queryset = Post.objects.order_by("-created_date")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


def post_list(request):
    "게시글 전체 목록"
    posts = Post.objects.order_by("-created_date")
    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, pk):
    "게시글 상세보기"
    post = get_object_or_404(Post, pk=pk)
    return render(request, "blog/post_detail.html", {"post": post})


def post_new(request):
    "새 게시글 작성"
    user = get_user_model()
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            author_id = request.POST.get("author_id")
            if author_id:
                try:
                    post.author = user.objects.get(pk=int(author_id))
                except (user.DoesNotExist, ValueError):
                    msg = "유효하지 않은 작성자 ID입니다: {}".format(author_id)
                    return render(
                        request,
                        "blog/error_page.html",
                        {"error_message": msg},
                        status=400,
                    )
            else:
                return render(
                    request,
                    "blog/error_page.html",
                    {"error_message": "작성자 ID가 제공되지 않았습니다."},
                    status=400,
                )

            post.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()
    return render(request, "blog/post_create.html", {"form": form})


def post_edit(request, pk):
    "게시글 수정"
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, "blog/post_edit.html", {"form": form})


def js_test(request):
    "API 테스트용"
    return render(request, "blog/js_test.html")

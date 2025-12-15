from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    객체의 소유자(author)만 수정/삭제할 수 있도록 허용
    그 외에는 읽기만 허용
    """

    def has_object_permission(self, request, view, obj):
        # 읽기권한은 모든 유저에 대해 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 쓰기권한은 객체의 소유자에게만 허용
        return obj.author == request.user

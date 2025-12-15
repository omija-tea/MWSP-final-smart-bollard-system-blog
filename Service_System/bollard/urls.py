"""
볼라드 시스템 URL 라우팅

REST API와 Template View URL을 정의합니다.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"settings", views.BollardSettingViewSet, basename="bollard-setting")

urlpatterns = [
    # YOLO 서버에서 검출 결과 수신
    path(
        "api/bollard/detection/",
        views.DetectionAPIView.as_view(),
        name="bollard_detection_api",
    ),
    # 볼라드 수동 제어
    path(
        "api/bollard/control/",
        views.BollardControlAPIView.as_view(),
        name="bollard_control_api",
    ),
    # 현재 상태 조회
    path(
        "api/bollard/state/",
        views.BollardStateAPIView.as_view(),
        name="bollard_state_api",
    ),
    # 시스템 전체 상태
    path(
        "api/bollard/status/",
        views.SystemStatusAPIView.as_view(),
        name="bollard_status_api",
    ),
    # ViewSet 라우터 (설정 CRUD, 로그 조회)
    path("api/bollard/", include(router.urls)),
    # 볼라드 설정 페이지 (메인)
    path("bollard/", views.bollard_setting_view, name="bollard_setting"),
    # 볼라드 대시보드
    path("bollard/dashboard/", views.bollard_dashboard, name="bollard_dashboard"),
]

import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BollardSetting, BollardState, DetectionLog
from .serializers import (
    DetectionResultSerializer,
    BollardSettingSerializer,
    BollardStateSerializer,
    DetectionLogSerializer,
    BollardControlSerializer,
)
from .utils.analyzer import get_analyzer
from .utils.blog_integration import (
    create_bollard_event_post,
    create_manual_control_post,
)
from .utils.grpc_client import (
    send_bollard_open,
    send_bollard_close,
    send_auto_mode,
    send_detection_result,
    set_system_active,
)

logger = logging.getLogger(__name__)


class DetectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DetectionResultSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        analyzer = get_analyzer()
        should_close, max_ratio, action = analyzer.analyze(
            detections=data["detections"],
            image_width=data["image_width"],
            image_height=data["image_height"],
        )

        send_detection_result(should_close)

        if action != "none":
            # Blog 포스트 생성
            post = create_bollard_event_post(
                image_base64=data.get("image"), action=action, occupy_ratio=max_ratio
            )

            log = DetectionLog.objects.create(
                detected=should_close,
                occupy_ratio_actual=max_ratio,
                action=action,
                post=post,
            )

            logger.info(f"Bollard action: {action}, ratio: {max_ratio:.1f}%")

        return Response(
            {
                "status": "processed",
                "should_close": should_close,
                "max_ratio": max_ratio,
                "action": action,
            }
        )


class BollardControlAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = BollardControlSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        action = serializer.validated_data["action"]
        analyzer = get_analyzer()
        setting = BollardSetting.get_active_setting()

        if action == "open":
            analyzer.force_open()
            send_bollard_open()
            set_system_active(False)
            create_manual_control_post("open", request.user.username)
            message = "볼라드가 열렸습니다"

        elif action == "close":
            analyzer.force_close()
            send_bollard_close()
            set_system_active(False)
            create_manual_control_post("close", request.user.username)
            message = "볼라드가 닫혔습니다"

        elif action == "auto":
            analyzer.set_auto_mode()
            send_auto_mode()
            set_system_active(True)
            message = "자동 모드로 전환되었습니다"

        elif action == "start_system":
            setting.is_active = True
            setting.save()
            analyzer.set_auto_mode()
            send_auto_mode()
            set_system_active(True)
            message = "시스템이 시작되었습니다"

        elif action == "stop_system":
            setting.is_active = False
            setting.save()
            set_system_active(False)
            message = "시스템이 정지되었습니다"

        return Response({"status": "success", "action": action, "message": message})


class BollardSettingViewSet(viewsets.ModelViewSet):
    queryset = BollardSetting.objects.all()
    serializer_class = BollardSettingSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["get"])
    def active(self, request):
        setting = BollardSetting.get_active_setting()
        serializer = self.get_serializer(setting)
        return Response(serializer.data)

    @action(detail=False, methods=["post", "patch"])
    def update_active(self, request):
        setting = BollardSetting.get_active_setting()
        serializer = self.get_serializer(setting, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "설정이 업데이트되었습니다",
                    "data": serializer.data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BollardStateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        state = BollardState.get_instance()
        serializer = BollardStateSerializer(state)
        return Response(serializer.data)


class DetectionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DetectionLog.objects.all().order_by("-timestamp")
    serializer_class = DetectionLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset[:100]


class SystemStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        setting = BollardSetting.get_active_setting()
        state = BollardState.get_instance()

        return Response(
            {
                "setting": BollardSettingSerializer(setting).data,
                "state": BollardStateSerializer(state).data,
            }
        )


def bollard_dashboard(request):
    setting = BollardSetting.get_active_setting()
    state = BollardState.get_instance()
    recent_logs = DetectionLog.objects.all().order_by("-timestamp")[:20]

    context = {
        "setting": setting,
        "state": state,
        "recent_logs": recent_logs,
        "system_status": "run" if setting.is_active else "stop",
    }
    return render(request, "bollard/dashboard.html", context)


def bollard_setting_view(request):
    setting = BollardSetting.get_active_setting()
    state = BollardState.get_instance()

    message = ""
    system_status = "run" if setting.is_active and not state.manual_mode else "stop"

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "bopen":
            # 볼라드 강제 열기
            analyzer = get_analyzer()
            analyzer.force_open()
            create_manual_control_post("open", request.user.username)
            message = "볼라드가 열렸습니다"

        elif action == "bclose":
            # 볼라드 강제 닫기
            analyzer = get_analyzer()
            analyzer.force_close()
            create_manual_control_post("close", request.user.username)
            message = "볼라드가 닫혔습니다"

        elif action == "server":
            # 서버 설정 변경
            occupy_ratio = request.POST.get("occupy_ratio")
            maintain_frame = request.POST.get("maintain_frame")
            target_object = request.POST.get("target_object")

            if occupy_ratio:
                setting.occupy_ratio = int(occupy_ratio)
            if maintain_frame:
                setting.maintain_frame = int(maintain_frame)
            if target_object:
                setting.target_object = int(target_object)
            setting.save()

            message = "서버 설정이 완료되었습니다"

        elif action == "stop_bollard":
            # 시스템 정지
            setting.is_active = False
            setting.save()
            system_status = "stop"
            message = "시스템이 정지되었습니다"

        elif action == "run_bollard":
            # 시스템 시작
            setting.is_active = True
            setting.save()
            analyzer = get_analyzer()
            analyzer.set_auto_mode()
            system_status = "run"
            message = "시스템이 시작되었습니다"

    context = {
        "setting": setting,
        "state": state,
        "system_status": system_status,
        "message": message,
    }
    return render(request, "bollard/setting.html", context)

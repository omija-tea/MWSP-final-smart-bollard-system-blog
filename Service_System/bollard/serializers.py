"""
볼라드 시스템 Serializers

YOLO 서버와의 통신 및 REST API를 위한 시리얼라이저입니다.
"""

from rest_framework import serializers
from .models import BollardSetting, BollardState, DetectionLog


class DetectionResultSerializer(serializers.Serializer):
    image = serializers.CharField(
        required=False, allow_blank=True, help_text="Base64 인코딩된 JPEG 이미지"
    )

    image_width = serializers.IntegerField(
        required=True, help_text="이미지 너비 (픽셀)"
    )
    image_height = serializers.IntegerField(
        required=True, help_text="이미지 높이 (픽셀)"
    )

    detections = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        allow_empty=True,
        help_text="검출된 객체 리스트",
    )

    # 타임스탬프
    timestamp = serializers.DateTimeField(
        required=False, help_text="검출 시점 타임스탬프 (생략 시 서버 시간 사용)"
    )

    def validate_detections(self, value):
        if not value:
            return value

        for det in value:
            if "class_id" not in det:
                raise serializers.ValidationError("Each detection must have 'class_id'")
            if "bbox" not in det:
                raise serializers.ValidationError("Each detection must have 'bbox'")
            bbox = det["bbox"]
            if not isinstance(bbox, list) or len(bbox) < 4:
                raise serializers.ValidationError("bbox must be [x1, y1, x2, y2]")
        return value


class BollardSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BollardSetting
        fields = [
            "id",
            "occupy_ratio",
            "maintain_frame",
            "target_object",
            "is_active",
            "raspberry_pi_host",
            "raspberry_pi_port",
            "grpc_server_port",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BollardStateSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    mode_display = serializers.SerializerMethodField()

    class Meta:
        model = BollardState
        fields = [
            "is_closed",
            "counter",
            "last_updated",
            "manual_mode",
            "status_display",
            "mode_display",
        ]
        read_only_fields = ["counter", "last_updated"]

    def get_status_display(self, obj):
        return "닫힘" if obj.is_closed else "열림"

    def get_mode_display(self, obj):
        return "수동" if obj.manual_mode else "자동"


class DetectionLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = DetectionLog
        fields = [
            "id",
            "timestamp",
            "detected",
            "occupy_ratio_actual",
            "action",
            "action_display",
            "post",
            "image",
        ]
        read_only_fields = ["id", "timestamp", "action_display"]


class BollardControlSerializer(serializers.Serializer):
    ACTION_CHOICES = [
        ("open", "볼라드 열기"),
        ("close", "볼라드 닫기"),
        ("auto", "자동 모드 전환"),
        ("start_system", "시스템 시작"),
        ("stop_system", "시스템 정지"),
    ]

    action = serializers.ChoiceField(choices=ACTION_CHOICES, help_text="수행할 동작")

    def validate_action(self, value):
        if value not in ["open", "close", "auto"]:
            raise serializers.ValidationError("Invalid action")
        return value


class SystemStatusSerializer(serializers.Serializer):
    setting = BollardSettingSerializer(read_only=True)
    state = BollardStateSerializer(read_only=True)
    recent_logs = DetectionLogSerializer(many=True, read_only=True)

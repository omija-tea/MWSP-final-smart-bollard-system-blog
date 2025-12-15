from django.db import models
from django.conf import settings
from blog.models import Post


class BollardSetting(models.Model):
    occupy_ratio = models.IntegerField(
        default=30, help_text="오토바이 차지 영역 퍼센트 (%)"
    )
    maintain_frame = models.IntegerField(
        default=10, help_text="볼라드 폐쇄 유지 프레임 수"
    )
    target_object = models.IntegerField(
        default=3, help_text="감지 대상 COCO 클래스 ID (3=오토바이)"
    )
    is_active = models.BooleanField(default=True, help_text="시스템 활성화 여부")

    raspberry_pi_host = models.CharField(
        max_length=100, default="192.168.0.100", help_text="라즈베리파이 IP 주소"
    )
    raspberry_pi_port = models.IntegerField(
        default=50051, help_text="라즈베리파이 gRPC 포트"
    )

    grpc_server_port = models.IntegerField(
        default=50051, help_text="Django gRPC 서버 포트"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "볼라드 설정"
        verbose_name_plural = "볼라드 설정"

    def __str__(self):
        return f"볼라드 설정 #{self.id} (점유율: {self.occupy_ratio}%, 유지프레임: {self.maintain_frame})"

    @classmethod
    def get_active_setting(cls):
        setting = cls.objects.filter(is_active=True).first()
        if not setting:
            setting = cls.objects.create(is_active=True)
        return setting


class BollardState(models.Model):
    is_closed = models.BooleanField(default=False, help_text="볼라드 닫힘 상태")
    counter = models.IntegerField(default=0, help_text="유지 프레임 카운터")
    last_updated = models.DateTimeField(auto_now=True)
    manual_mode = models.BooleanField(default=False, help_text="수동 제어 모드")

    class Meta:
        verbose_name = "볼라드 상태"
        verbose_name_plural = "볼라드 상태"

    def __str__(self):
        status = "닫힘" if self.is_closed else "열림"
        mode = "수동" if self.manual_mode else "자동"
        return f"볼라드 상태: {status} ({mode} 모드)"

    @classmethod
    def get_instance(cls):
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance


class DetectionLog(models.Model):
    ACTION_CHOICES = [
        ("open", "볼라드 열림"),
        ("close", "볼라드 닫힘"),
        ("none", "변화 없음"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    detected = models.BooleanField(help_text="객체 감지 여부")
    occupy_ratio_actual = models.FloatField(
        null=True, blank=True, help_text="실제 측정된 점유율 (%)"
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, default="none")

    post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detection_logs",
        help_text="볼라드 이벤트 시 생성된 포스트",
    )

    image = models.ImageField(
        upload_to="detection_logs/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text="감지 시점 이미지",
    )

    class Meta:
        verbose_name = "감지 로그"
        verbose_name_plural = "감지 로그"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.timestamp}] 감지: {self.detected}, 동작: {self.action}"

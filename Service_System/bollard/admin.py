from django.contrib import admin
from .models import BollardSetting, DetectionLog


@admin.register(BollardSetting)
class BollardSettingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "occupy_ratio",
        "maintain_frame",
        "target_object",
        "is_active",
        "updated_at",
    )
    list_filter = ("is_active",)


@admin.register(DetectionLog)
class DetectionLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "timestamp",
        "detected",
        "occupy_ratio_actual",
        "action",
        "post",
    )
    list_filter = ("detected", "action", "timestamp")
    ordering = ("-timestamp",)

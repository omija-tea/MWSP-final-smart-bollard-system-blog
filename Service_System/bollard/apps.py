import os
import threading
from django.apps import AppConfig


class BollardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bollard"
    verbose_name = "스마트 볼라드 시스템"

    _grpc_started = False

    def ready(self):
        # 이중호출 방지
        if os.environ.get("RUN_MAIN") != "true":
            return

        if BollardConfig._grpc_started:
            return

        from bollard.models import BollardSetting

        def start_grpc():
            try:
                from bollard.utils.grpc_client import start_grpc_server

                try:
                    setting = BollardSetting.objects.first()
                    grpc_port = setting.grpc_server_port if setting else 50051
                except Exception:
                    grpc_port = 50051

                start_grpc_server(port=grpc_port)
                BollardConfig._grpc_started = True

            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Failed to start gRPC server: {e}")

        thread = threading.Thread(target=start_grpc, daemon=True)
        thread.start()

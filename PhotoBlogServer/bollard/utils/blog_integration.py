import base64
import logging
from typing import Optional
from io import BytesIO

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from blog.models import Post

logger = logging.getLogger(__name__)


def create_bollard_event_post(
    image_base64: Optional[str],
    action: str,
    occupy_ratio: float = 0.0,
    author_username: str = "yolo_edge",
) -> Optional[Post]:
    User = get_user_model()

    try:
        author = User.objects.get(username=author_username)
    except User.DoesNotExist:
        author = User.objects.filter(is_superuser=True).first()
        if not author:
            author = User.objects.create_user(
                username="yolo_edge",
                email="yolo@system.local",
                password=User.objects.make_random_password(),
                is_active=True,
            )
            logger.info(f"Created yolo_edge user: {author.id}")

    timestamp = timezone.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    if action == "close":
        title = f"🚨 볼라드 닫힘 - {timestamp_str}"
        text = f"""오토바이가 감지되어 볼라드가 닫혔습니다.

📊 감지 정보:
- 시간: {timestamp_str}
- 점유율: {occupy_ratio:.1f}%
- 동작: 볼라드 닫힘 (차량 진입 차단)

🔒 시스템 자동 기록"""
    else:  # open
        title = f"✅ 볼라드 열림 - {timestamp_str}"
        text = f"""오토바이가 더 이상 감지되지 않아 볼라드가 열렸습니다.

📊 감지 정보:
- 시간: {timestamp_str}
- 점유율: {occupy_ratio:.1f}%
- 동작: 볼라드 열림 (통행 허용)

🔓 시스템 자동 기록"""

    try:
        post = Post(
            author=author,
            title=title,
            text=text,
            created_date=timestamp,
        )

        if image_base64:
            try:
                image_data = base64.b64decode(image_base64)
                filename = f"bollard_{action}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
                post.image.save(filename, ContentFile(image_data), save=False)
            except Exception as e:
                logger.error(f"Failed to save image: {e}")

        post.save()
        post.publish()

        logger.info(f"Created bollard event post: {post.id} - {action}")
        return post

    except Exception as e:
        logger.error(f"Failed to create bollard event post: {e}")
        return None


def create_manual_control_post(action: str, operator_username: str) -> Optional[Post]:
    User = get_user_model()

    try:
        operator = User.objects.get(username=operator_username)
    except User.DoesNotExist:
        operator = User.objects.filter(is_superuser=True).first()
        if not operator:
            logger.error("No operator user found")
            return None

    timestamp = timezone.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    if action == "close":
        title = f"🔒 볼라드 수동 닫힘 - {timestamp_str}"
        text = f"""관리자가 볼라드를 수동으로 닫았습니다.

📋 제어 정보:
- 시간: {timestamp_str}
- 조작자: {operator_username}
- 동작: 볼라드 수동 닫힘

⚠️ 수동 제어 기록"""
    else:
        title = f"🔓 볼라드 수동 열림 - {timestamp_str}"
        text = f"""관리자가 볼라드를 수동으로 열었습니다.

📋 제어 정보:
- 시간: {timestamp_str}
- 조작자: {operator_username}
- 동작: 볼라드 수동 열림

⚠️ 수동 제어 기록"""

    try:
        post = Post(
            author=operator,
            title=title,
            text=text,
            created_date=timestamp,
        )

        placeholder_image = create_placeholder_image()
        filename = f"manual_{action}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        post.image.save(filename, ContentFile(placeholder_image), save=False)

        post.save()
        post.publish()

        logger.info(f"Created manual control post: {post.id} - {action}")
        return post

    except Exception as e:
        logger.error(f"Failed to create manual control post: {e}")
        return None


def create_placeholder_image() -> bytes:
    jpeg_1x1_gray = bytes(
        [
            0xFF,
            0xD8,
            0xFF,
            0xE0,
            0x00,
            0x10,
            0x4A,
            0x46,
            0x49,
            0x46,
            0x00,
            0x01,
            0x01,
            0x00,
            0x00,
            0x01,
            0x00,
            0x01,
            0x00,
            0x00,
            0xFF,
            0xDB,
            0x00,
            0x43,
            0x00,
            0x08,
            0x06,
            0x06,
            0x07,
            0x06,
            0x05,
            0x08,
            0x07,
            0x07,
            0x07,
            0x09,
            0x09,
            0x08,
            0x0A,
            0x0C,
            0x14,
            0x0D,
            0x0C,
            0x0B,
            0x0B,
            0x0C,
            0x19,
            0x12,
            0x13,
            0x0F,
            0x14,
            0x1D,
            0x1A,
            0x1F,
            0x1E,
            0x1D,
            0x1A,
            0x1C,
            0x1C,
            0x20,
            0x24,
            0x2E,
            0x27,
            0x20,
            0x22,
            0x2C,
            0x23,
            0x1C,
            0x1C,
            0x28,
            0x37,
            0x29,
            0x2C,
            0x30,
            0x31,
            0x34,
            0x34,
            0x34,
            0x1F,
            0x27,
            0x39,
            0x3D,
            0x38,
            0x32,
            0x3C,
            0x2E,
            0x33,
            0x34,
            0x32,
            0xFF,
            0xC0,
            0x00,
            0x0B,
            0x08,
            0x00,
            0x01,
            0x00,
            0x01,
            0x01,
            0x01,
            0x11,
            0x00,
            0xFF,
            0xC4,
            0x00,
            0x1F,
            0x00,
            0x00,
            0x01,
            0x05,
            0x01,
            0x01,
            0x01,
            0x01,
            0x01,
            0x01,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x01,
            0x02,
            0x03,
            0x04,
            0x05,
            0x06,
            0x07,
            0x08,
            0x09,
            0x0A,
            0x0B,
            0xFF,
            0xC4,
            0x00,
            0xB5,
            0x10,
            0x00,
            0x02,
            0x01,
            0x03,
            0x03,
            0x02,
            0x04,
            0x03,
            0x05,
            0x05,
            0x04,
            0x04,
            0x00,
            0x00,
            0x01,
            0x7D,
            0x01,
            0x02,
            0x03,
            0x00,
            0x04,
            0x11,
            0x05,
            0x12,
            0x21,
            0x31,
            0x41,
            0x06,
            0x13,
            0x51,
            0x61,
            0x07,
            0x22,
            0x71,
            0x14,
            0x32,
            0x81,
            0x91,
            0xA1,
            0x08,
            0x23,
            0x42,
            0xB1,
            0xC1,
            0x15,
            0x52,
            0xD1,
            0xF0,
            0x24,
            0x33,
            0x62,
            0x72,
            0x82,
            0x09,
            0x0A,
            0x16,
            0x17,
            0x18,
            0x19,
            0x1A,
            0x25,
            0x26,
            0x27,
            0x28,
            0x29,
            0x2A,
            0x34,
            0x35,
            0x36,
            0x37,
            0x38,
            0x39,
            0x3A,
            0x43,
            0x44,
            0x45,
            0x46,
            0x47,
            0x48,
            0x49,
            0x4A,
            0x53,
            0x54,
            0x55,
            0x56,
            0x57,
            0x58,
            0x59,
            0x5A,
            0x63,
            0x64,
            0x65,
            0x66,
            0x67,
            0x68,
            0x69,
            0x6A,
            0x73,
            0x74,
            0x75,
            0x76,
            0x77,
            0x78,
            0x79,
            0x7A,
            0x83,
            0x84,
            0x85,
            0x86,
            0x87,
            0x88,
            0x89,
            0x8A,
            0x92,
            0x93,
            0x94,
            0x95,
            0x96,
            0x97,
            0x98,
            0x99,
            0x9A,
            0xA2,
            0xA3,
            0xA4,
            0xA5,
            0xA6,
            0xA7,
            0xA8,
            0xA9,
            0xAA,
            0xB2,
            0xB3,
            0xB4,
            0xB5,
            0xB6,
            0xB7,
            0xB8,
            0xB9,
            0xBA,
            0xC2,
            0xC3,
            0xC4,
            0xC5,
            0xC6,
            0xC7,
            0xC8,
            0xC9,
            0xCA,
            0xD2,
            0xD3,
            0xD4,
            0xD5,
            0xD6,
            0xD7,
            0xD8,
            0xD9,
            0xDA,
            0xE1,
            0xE2,
            0xE3,
            0xE4,
            0xE5,
            0xE6,
            0xE7,
            0xE8,
            0xE9,
            0xEA,
            0xF1,
            0xF2,
            0xF3,
            0xF4,
            0xF5,
            0xF6,
            0xF7,
            0xF8,
            0xF9,
            0xFA,
            0xFF,
            0xDA,
            0x00,
            0x08,
            0x01,
            0x01,
            0x00,
            0x00,
            0x3F,
            0x00,
            0xFB,
            0xD5,
            0xDB,
            0x20,
            0xA8,
            0xF1,
            0x7E,
            0xFF,
            0xD9,
        ]
    )
    return jpeg_1x1_gray

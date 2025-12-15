import datetime
import os
import pathlib
import base64
import time

import cv2
import requests
from dotenv import load_dotenv

BASE_DIR = pathlib.Path(__file__).resolve().parent

load_dotenv(dotenv_path=BASE_DIR / ".env")


class ChangeDetection:
    result_prev = []
    HOST = os.getenv("HOST")
    token = os.getenv("DJANGO_TOKEN")
    FP_tolerance = 0.5

    # 볼라드 API 설정
    BOLLARD_API_ENABLED = os.getenv("BOLLARD_API_ENABLED", "true").lower() == "true"
    last_bollard_send_time = 0
    BOLLARD_SEND_INTERVAL = 1

    def __init__(self, names):
        self.result_prev = [0 for i in range(len(names))]
        print(self.token)

    def add(self, names, detected_current, save_dir, image, detections=None):
        self.title = ""
        self.text = ""
        change_flag = 0
        i = 0
        while i < len(self.result_prev):
            if self.result_prev[i] != detected_current[i]:
                if self.result_prev[i] <= detected_current[i]:
                    self.result_prev[i] += self.FP_tolerance
                    if self.result_prev[i] > 1:
                        self.result_prev[i] = 1
                else:
                    self.result_prev[i] = 0

                if self.result_prev[i] == 1:
                    change_flag = 1
                    self.title = names[i]
                    self.text += names[i] + ","
            i += 1
        # 볼라드 API 전송 (0.25초마다)
        if self.BOLLARD_API_ENABLED and detections is not None:
            current_time = time.time()
            if current_time - self.last_bollard_send_time >= self.BOLLARD_SEND_INTERVAL:
                self.send_to_bollard_api(detections, image)
                self.last_bollard_send_time = current_time

    def send(self, save_dir, image):
        now = datetime.datetime.now()
        now.isoformat()

        today = datetime.datetime.now()
        save_path = (
            os.getcwd()
            / save_dir
            / "detected"
            / str(today.year)
            / str(today.month)
            / str(today.day)
        )
        pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

        full_path = save_path / "{0}-{1}-{2}-{3}.jpg".format(
            today.hour, today.minute, today.second, today.microsecond
        )
        dst = cv2.resize(image, dsize=(320, 240), interpolation=cv2.INTER_AREA)
        cv2.imwrite(full_path, dst)
        # 인증이 필요한 요청에 아래의 headers를 붙임
        headers = {"Authorization": f"Token {self.token}", "Accept": "application/json"}
        # Post Create
        data = {
            "title": self.title,
            "text": self.text,
            "created_date": now,
            "published_date": now,
        }
        file = {"image": open(full_path, "rb")}
        res = requests.post(
            self.HOST + "/api_root/Post/", data=data, files=file, headers=headers
        )
        print(res)

    def send_to_bollard_api(self, detections, image):
        """볼라드 API로 검출 결과 전송"""
        if not self.token or not self.HOST:
            return

        headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
        }

        height, width = image.shape[:2]

        # 이미지 base64 인코딩 (검출 시에만)
        image_base64 = ""
        if detections:
            try:
                _, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 70])
                image_base64 = base64.b64encode(encoded).decode("utf-8")
            except:
                pass

        payload = {
            "detections": detections if detections else [],
            "image_width": width,
            "image_height": height,
        }

        # 이미지가 있을 때만 포함
        if image_base64:
            payload["image"] = image_base64

        try:
            requests.post(
                self.HOST + "/api/bollard/detection/",
                json=payload,
                headers=headers,
                timeout=1,
            )
        except:
            pass

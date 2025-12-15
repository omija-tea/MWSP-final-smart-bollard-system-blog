from typing import List, Dict, Any, Tuple
from bollard.models import BollardSetting, BollardState


class BollardAnalyzer:
    """
    볼라드 분석기 - YOLO 검출 결과를 분석하여 볼라드 열림/닫힘 판단

    알고리즘:
    1. 검출된 객체 중 target_object (오토바이=3)만 필터링
    2. 각 객체의 화면 점유율 계산 (바운딩 박스 면적 / 전체 이미지 면적)
    3. 최대 점유율이 occupy_ratio 임계값을 초과하면 카운터를 maintain_frame으로 설정
    4. 카운터 > 0이면 볼라드 닫힘 유지, 아니면 열림
    """

    def __init__(self):
        pass

    def analyze(
        self, detections: List[Dict[str, Any]], image_width: int, image_height: int
    ) -> Tuple[bool, float, str]:
        """
        검출 결과 분석

        Args:
            detections: YOLO 검출 결과 리스트
                각 항목: {
                    "class_id": int,      # COCO 클래스 ID
                    "confidence": float,  # 신뢰도 (0~1)
                    "bbox": [x1, y1, x2, y2]  # 바운딩 박스 좌표
                }
            image_width: 이미지 너비 (픽셀)
            image_height: 이미지 높이 (픽셀)

        Returns:
            Tuple[bool, float, str]:
                - should_close: 볼라드를 닫아야 하는지 여부
                - max_occupy_ratio: 감지된 최대 점유율 (%)
                - action: 수행할 액션 ("open", "close", "none")
        """
        setting = BollardSetting.get_active_setting()
        state = BollardState.get_instance()

        if state.manual_mode:
            return (state.is_closed, 0.0, "none")

        occupy_ratio = setting.occupy_ratio
        maintain_frame = setting.maintain_frame
        target_object = setting.target_object

        img_area = image_width * image_height
        if img_area == 0:
            return (False, 0.0, "none")

        # 타겟 객체 필터링 및 최대 점유율 계산
        max_ratio = 0.0
        for det in detections:
            if det.get("class_id") == target_object:
                bbox = det.get("bbox", [0, 0, 0, 0])
                if len(bbox) >= 4:
                    x1, y1, x2, y2 = bbox[:4]
                    box_area = (x2 - x1) * (y2 - y1)
                    current_ratio = (box_area / img_area) * 100
                    if current_ratio > max_ratio:
                        max_ratio = current_ratio

        if max_ratio > occupy_ratio:
            state.counter = maintain_frame
        else:
            state.counter = max(0, state.counter - 1)

        should_close = state.counter > 0

        action = "none"
        if should_close and not state.is_closed:
            action = "close"
            state.is_closed = True
        elif not should_close and state.is_closed:
            action = "open"
            state.is_closed = False

        state.save()

        return (should_close, max_ratio, action)

    def force_open(self) -> str:
        state = BollardState.get_instance()
        state.is_closed = True
        state.manual_mode = True
        state.save()
        return "close"

    def set_auto_mode(self) -> None:
        state = BollardState.get_instance()
        state.manual_mode = False
        state.save()

    def reset_state(self) -> None:
        state = BollardState.get_instance()
        state.is_closed = False
        state.counter = 0
        state.manual_mode = False
        state.save()


_analyzer_instance = None


def get_analyzer() -> BollardAnalyzer:
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = BollardAnalyzer()
    return _analyzer_instance

import grpc
import logging
import threading
import queue
from typing import Optional
from concurrent import futures

from bollard.grpc_proto.result_pb2 import Req, Res, OptVal

logger = logging.getLogger(__name__)


class BollardCommandQueue:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._result_queue = queue.Queue()
                    cls._instance._option_queue = queue.Queue()
                    cls._instance._current_result = False
        return cls._instance

    def put_result(self, should_close: bool):
        self._current_result = should_close

    def get_current_result(self) -> bool:
        return self._current_result

    def put_option(self, opt_val: OptVal):
        try:
            self._option_queue.put_nowait(opt_val)
        except queue.Full:
            pass

    def get_option(self, timeout: float = 1.0) -> Optional[OptVal]:
        try:
            return self._option_queue.get(timeout=timeout)
        except queue.Empty:
            return None


class BollardGrpcServicer:
    def __init__(self):
        self.command_queue = BollardCommandQueue()
        self._system_active = threading.Event()

    def set_system_active(self, active: bool):
        if active:
            self._system_active.set()
        else:
            self._system_active.clear()

    def is_system_active(self) -> bool:
        return self._system_active.is_set()

    def Require(self, request, context):
        logger.info("Raspberry Pi connected to Require stream")

        while context.is_active() and self._system_active.is_set():
            should_close = self.command_queue.get_current_result()
            yield Res(response=should_close)

            import time

            time.sleep(0.1)

        logger.info("Require stream ended")

    def Option(self, request, context):
        logger.info("Raspberry Pi connected to Option stream")

        while context.is_active() and not self._system_active.is_set():
            opt_val = self.command_queue.get_option(timeout=1.0)
            if opt_val:
                yield opt_val

                if opt_val.letsgo_flag and opt_val.letsgo:
                    self._system_active.set()
                    break

        logger.info("Option stream ended")


_grpc_servicer: Optional[BollardGrpcServicer] = None
_grpc_server = None
_grpc_lock = threading.Lock()


def get_grpc_servicer() -> BollardGrpcServicer:
    global _grpc_servicer
    if _grpc_servicer is None:
        _grpc_servicer = BollardGrpcServicer()
    return _grpc_servicer


def start_grpc_server(port: int = 50051) -> bool:
    global _grpc_server, _grpc_servicer

    with _grpc_lock:
        if _grpc_server is not None:
            logger.warning("gRPC server already running")
            return False

        try:
            from bollard.grpc_proto.result_pb2_grpc import add_ResultServicer_to_server

            _grpc_servicer = get_grpc_servicer()
            _grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            add_ResultServicer_to_server(_grpc_servicer, _grpc_server)
            _grpc_server.add_insecure_port(f"[::]:{port}")
            _grpc_server.start()

            logger.info(f"gRPC server started on port {port}")
            return True

        except Exception as e:
            logger.error(f"Failed to start gRPC server: {e}")
            return False


def stop_grpc_server():
    global _grpc_server

    with _grpc_lock:
        if _grpc_server:
            _grpc_server.stop(grace=5)
            _grpc_server = None
            logger.info("gRPC server stopped")


# 볼라드 제어 함수들 (Django 뷰에서 호출)
def send_bollard_open():
    servicer = get_grpc_servicer()
    command_queue = BollardCommandQueue()

    opt_val = OptVal(manual_flag=True, manual=True, letsgo_flag=False, letsgo=False)
    command_queue.put_option(opt_val)
    logger.info("Bollard OPEN command queued")


def send_bollard_close():
    servicer = get_grpc_servicer()
    command_queue = BollardCommandQueue()

    opt_val = OptVal(manual_flag=True, manual=False, letsgo_flag=False, letsgo=False)
    command_queue.put_option(opt_val)
    logger.info("Bollard CLOSE command queued")


def send_auto_mode():
    servicer = get_grpc_servicer()
    command_queue = BollardCommandQueue()

    opt_val = OptVal(manual_flag=False, manual=False, letsgo_flag=True, letsgo=True)
    command_queue.put_option(opt_val)
    servicer.set_system_active(True)
    logger.info("Auto mode command queued")


def send_detection_result(should_close: bool):
    command_queue = BollardCommandQueue()
    command_queue.put_result(should_close)


def set_system_active(active: bool):
    servicer = get_grpc_servicer()
    servicer.set_system_active(active)

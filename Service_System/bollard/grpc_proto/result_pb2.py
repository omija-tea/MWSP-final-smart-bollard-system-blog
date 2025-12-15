# -*- coding: utf-8 -*-
# Generated protocol buffer code for bollard system

from dataclasses import dataclass
from typing import Optional


@dataclass
class Req:
    request: int = 0

    def SerializeToString(self) -> bytes:
        # Field 1, varint type (wire type 0)
        if self.request != 0:
            return bytes([0x08]) + self._encode_varint(self.request)
        return b""

    @classmethod
    def FromString(cls, data: bytes) -> "Req":
        if not data:
            return cls()
        idx = 0
        request = 0
        while idx < len(data):
            tag = data[idx]
            idx += 1
            field_num = tag >> 3
            wire_type = tag & 0x07
            if field_num == 1 and wire_type == 0:
                request, idx = cls._decode_varint(data, idx)
        return cls(request=request)

    @staticmethod
    def _encode_varint(value: int) -> bytes:
        bits = value & 0x7F
        value >>= 7
        result = b""
        while value:
            result += bytes([0x80 | bits])
            bits = value & 0x7F
            value >>= 7
        result += bytes([bits])
        return result

    @staticmethod
    def _decode_varint(data: bytes, idx: int) -> tuple:
        result = 0
        shift = 0
        while True:
            b = data[idx]
            idx += 1
            result |= (b & 0x7F) << shift
            if not (b & 0x80):
                break
            shift += 7
        return result, idx


@dataclass
class Res:
    response: bool = False

    def SerializeToString(self) -> bytes:
        if self.response:
            return bytes([0x08, 0x01])
        return bytes([0x08, 0x00])

    @classmethod
    def FromString(cls, data: bytes) -> "Res":
        if not data:
            return cls()
        idx = 0
        response = False
        while idx < len(data):
            if idx >= len(data):
                break
            tag = data[idx]
            idx += 1
            field_num = tag >> 3
            if field_num == 1:
                if idx < len(data):
                    response = data[idx] != 0
                    idx += 1
        return cls(response=response)


@dataclass
class OptVal:
    manual_flag: bool = False
    manual: bool = False
    letsgo_flag: bool = False
    letsgo: bool = False

    def SerializeToString(self) -> bytes:
        result = b""
        # Field 1: manual_flag
        result += bytes([0x08, 0x01 if self.manual_flag else 0x00])
        # Field 2: manual
        result += bytes([0x10, 0x01 if self.manual else 0x00])
        # Field 3: letsgo_flag
        result += bytes([0x18, 0x01 if self.letsgo_flag else 0x00])
        # Field 4: letsgo
        result += bytes([0x20, 0x01 if self.letsgo else 0x00])
        return result

    @classmethod
    def FromString(cls, data: bytes) -> "OptVal":
        if not data:
            return cls()
        manual_flag = False
        manual = False
        letsgo_flag = False
        letsgo = False
        idx = 0
        while idx < len(data):
            if idx >= len(data):
                break
            tag = data[idx]
            idx += 1
            field_num = tag >> 3
            if idx < len(data):
                value = data[idx] != 0
                idx += 1
                if field_num == 1:
                    manual_flag = value
                elif field_num == 2:
                    manual = value
                elif field_num == 3:
                    letsgo_flag = value
                elif field_num == 4:
                    letsgo = value
        return cls(
            manual_flag=manual_flag,
            manual=manual,
            letsgo_flag=letsgo_flag,
            letsgo=letsgo,
        )


_REQ = Req
_RES = Res
_OPTVAL = OptVal

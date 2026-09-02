# -*- coding: utf-8 -*-
"""Tiny byte helpers for MTEF parsing."""


class Helper:
    @staticmethod
    def bytes2int(data):
        if data is None:
            return None
        if isinstance(data, int):
            return data
        if not data:
            return None
        return int.from_bytes(data, byteorder="little", signed=False)

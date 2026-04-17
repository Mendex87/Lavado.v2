from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PlcAddress:
    db: int
    byte: int
    type: str
    bit: int | None = None


class Snap7PlcClient:
    def __init__(self, host: str, rack: int, slot: int):
        self.host = host
        self.rack = rack
        self.slot = slot
        self._client = None
        self._util = None

    def connect(self) -> None:
        try:
            import snap7  # type: ignore
            from snap7 import util  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                'python-snap7 no está instalado. Próximo paso: instalarlo y conectar este poller al S7 real.'
            ) from exc
        self._client = snap7.client.Client()
        self._client.connect(self.host, self.rack, self.slot)
        self._util = util

    def ensure_connected(self) -> None:
        if self._client is None:
            self.connect()

    def read(self, address: PlcAddress) -> Any:
        self.ensure_connected()
        assert self._client is not None
        assert self._util is not None

        if address.type == 'real':
            data = self._client.db_read(address.db, address.byte, 4)
            return float(self._util.get_real(data, 0))
        if address.type == 'int':
            data = self._client.db_read(address.db, address.byte, 2)
            return int(self._util.get_int(data, 0))
        if address.type == 'bool':
            if address.bit is None:
                raise ValueError('Dirección bool requiere bit')
            data = self._client.db_read(address.db, address.byte, 1)
            return bool(self._util.get_bool(data, 0, address.bit))
        raise ValueError(f'Tipo PLC no soportado: {address.type}')

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.disconnect()
            finally:
                self._client.destroy()
                self._client = None

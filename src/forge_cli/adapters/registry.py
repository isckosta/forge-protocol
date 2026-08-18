"""In-memory registry of packaged Harness Drivers."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping

from forge_cli.adapters.driver import HarnessDriver


class UnknownAdapterError(RuntimeError):
    code = "E_FORGE_ADAPTER_UNKNOWN"


class DuplicateAdapterError(RuntimeError):
    code = "E_FORGE_ADAPTER_DUPLICATE"


@dataclass(frozen=True, init=False)
class AdapterRegistry:
    _drivers: tuple[HarnessDriver, ...]
    _drivers_by_id: Mapping[str, HarnessDriver]

    def __init__(self, drivers: Iterable[HarnessDriver]) -> None:
        drivers_by_id: dict[str, HarnessDriver] = {}
        for driver in drivers:
            adapter_id = driver.manifest.adapter_id
            if adapter_id in drivers_by_id:
                raise DuplicateAdapterError(f"Duplicate Adapter id: {adapter_id}")
            drivers_by_id[adapter_id] = driver

        ordered_drivers = tuple(
            sorted(drivers_by_id.values(), key=lambda driver: driver.manifest.adapter_id)
        )
        object.__setattr__(self, "_drivers", ordered_drivers)
        object.__setattr__(
            self,
            "_drivers_by_id",
            MappingProxyType({driver.manifest.adapter_id: driver for driver in ordered_drivers}),
        )

    def list(self) -> tuple[HarnessDriver, ...]:
        return self._drivers

    def get(self, adapter_id: str) -> HarnessDriver:
        try:
            return self._drivers_by_id[adapter_id]
        except KeyError as error:
            raise UnknownAdapterError(f"Unknown Adapter id: {adapter_id}") from error

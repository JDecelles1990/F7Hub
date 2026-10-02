"""Open the technician reference overlay through its launch gateway."""

from __future__ import annotations

from typing import Protocol
from f7hub.infrastructure.altf7hub_gateway import AltF7HubOpenError


class AltF7HubGateway(Protocol):
    def show_guide(self) -> str: ...


class AltF7HubService:
    def __init__(self, gateway: AltF7HubGateway) -> None:
        self.gateway = gateway

    def show_guide(self) -> str:
        return self.gateway.show_guide()

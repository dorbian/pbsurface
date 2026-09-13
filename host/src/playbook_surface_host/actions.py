"""Allowlisted process actions with no shell interpretation."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from .model import Action


class UnknownAction(KeyError):
    """Raised when a client requests an action not defined by the endpoint."""


@dataclass(frozen=True)
class ActionResult:
    action_id: str
    pid: int


class ActionExecutor:
    def __init__(self, actions: dict[str, Action]) -> None:
        self._actions = dict(actions)

    def run(self, action_id: str) -> ActionResult:
        try:
            action = self._actions[action_id]
        except KeyError as exc:
            raise UnknownAction(action_id) from exc
        process = subprocess.Popen(
            list(action.command),
            cwd=action.cwd,
            shell=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        return ActionResult(action_id=action.action_id, pid=process.pid)


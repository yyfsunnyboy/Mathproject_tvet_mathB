# -*- coding: utf-8 -*-
"""Execution boundary for bootstrap/healer isolated runs."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class ExecutionPolicy:
  """Sandbox policy gate for candidate code execution."""

  workspace_root: Path
  allow_network: bool = False
  timeout_seconds: float = 5.0
  max_memory_mb: int = 256
  allow_subprocess: bool = False

  def assert_path_allowed(self, path: Path) -> None:
      resolved = path.resolve()
      root = self.workspace_root.resolve()
      if root not in resolved.parents and resolved != root:
          raise PermissionError(f"execution_boundary_violation:{resolved}")

  def run_callable(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
      if self.allow_subprocess:
          raise PermissionError("subprocess_not_allowed_by_default")
      return fn(*args, **kwargs)


def py_compile_in_workspace(policy: ExecutionPolicy, file_path: Path) -> None:
    policy.assert_path_allowed(file_path)
    import py_compile

    py_compile.compile(str(file_path), doraise=True)

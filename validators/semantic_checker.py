# -*- coding: utf-8 -*-
from validators.base_checker import BaseChecker
from typing import Any, Tuple, Dict

class SemanticChecker(BaseChecker):
    """
    Semantic Checker class for semantic validation checks.
    """
    def check_semantic(self, payload: Dict[str, Any], spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Runs semantic validations and returns (can_continue, error_json).
        """
        # Call BaseChecker check
        return self.check(payload, spec)

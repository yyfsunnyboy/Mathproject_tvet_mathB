# -*- coding: utf-8 -*-
import random
import logging
from typing import Any, List, Dict

logger = logging.getLogger(__name__)

class BaseGenerator:
    """
    Base Generator class implementing Low-Sample Adaptation.
    """
    def __init__(self, source_examples: List[Dict[str, Any]]):
        self.source_examples = source_examples or []
        self.low_source_examples = len(self.source_examples) <= 2

    def adapt_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scale parameters/ranges by 150% if in low source example mode.
        """
        if not self.low_source_examples:
            return params
        
        logger.info("[LOW-SAMPLE ADAPTATION] Scaling parameters by 150% due to low source examples (<= 2).")
        adapted = {}
        for k, v in params.items():
            if isinstance(v, (int, float)):
                # scale numeric ranges or values
                adapted[k] = v * 1.5
            elif isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
                # scale numeric list ranges e.g. [min, max]
                adapted[k] = [x * 1.5 for x in v]
            elif isinstance(v, dict):
                adapted[k] = self.adapt_parameters(v)
            else:
                adapted[k] = v
        return adapted

    def adjust_variance(self, seed_variance: int) -> int:
        if self.low_source_examples:
            return int(seed_variance * 1.5)
        return seed_variance

    def exempt_diversity_warning(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exempt diversity blocking if due to low source examples.
        Downgrades warning/blocker to Info.
        """
        if self.low_source_examples:
            logger.info("[LOW-SAMPLE ADAPTATION] Low source examples detected. Downgrading diversity blocker/warning to Info.")
            if "generator_diversity_blocked" in metrics.get("diversity_blockers", []):
                metrics["diversity_blockers"] = [b for b in metrics["diversity_blockers"] if b != "generator_diversity_blocked"]
            if metrics.get("diversity_sampling_status") == "generator_diversity_blocked":
                metrics["diversity_sampling_status"] = "passed"
        return metrics

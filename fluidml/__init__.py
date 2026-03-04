"""
FluidML package.

Public API is intentionally small and stable for downstream users.
"""

from .config import FluidMLConfig, HLSBackendConfig
from .framework import FluidMLFramework, create_sample_config, quick_start_example

__all__ = [
    "HLSBackendConfig",
    "FluidMLConfig",
    "FluidMLFramework",
    "create_sample_config",
    "quick_start_example",
]

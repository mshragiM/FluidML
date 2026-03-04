"""
Compatibility wrapper for legacy imports.

Use `fluidml` package imports directly for new projects.
"""

from fluidml.codegen import CodeGenerator, Jinja2HLSCodeGenerator
from fluidml.config import FluidMLConfig, HLSBackendConfig
from fluidml.data import DataManager
from fluidml.framework import FluidMLFramework, create_sample_config, quick_start_example
from fluidml.training import ModelTrainer

# Legacy aliases preserved for older integrations.
RFConfig = FluidMLConfig
RFFramework = FluidMLFramework

__all__ = [
    "CodeGenerator",
    "Jinja2HLSCodeGenerator",
    "DataManager",
    "FluidMLConfig",
    "FluidMLFramework",
    "HLSBackendConfig",
    "ModelTrainer",
    "RFConfig",
    "RFFramework",
    "create_sample_config",
    "quick_start_example",
]

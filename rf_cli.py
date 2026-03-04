#!/usr/bin/env python3
"""Compatibility wrapper for the FluidML CLI."""

import sys

from fluidml.cli import main


if __name__ == "__main__":
    sys.exit(main())

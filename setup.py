#!/usr/bin/env python3

from setuptools import setup, find_packages


setup(
    name="houston",
    packages=find_packages(),
    scripts=[
        "scripts/houstonv"
        ],
    version="0.1.0",
    description="Telemetry & event logging library"
    )

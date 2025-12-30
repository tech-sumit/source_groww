#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="source_groww",
    version="0.1.0",
    description="Airbyte source connector for Groww Trade API",
    author="Sumit Agrawal",
    packages=find_packages(),
    install_requires=[
        "airbyte-cdk>=0.50.0",
    ],
    package_data={
        "source_groww": ["spec.yaml", "schemas/*.json"],
    },
    entry_points={
        "console_scripts": [
            "source-groww=source_groww.run:run",
        ],
    },
)

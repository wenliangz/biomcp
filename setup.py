"""Setup configuration for wedaita-biomcp."""

from setuptools import setup, find_packages

setup(
    name="wedaita-biomcp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "httpx>=0.24.0",
    ],
    python_requires=">=3.9",
) 
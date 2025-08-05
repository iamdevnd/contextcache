from setuptools import setup, find_packages

setup(
    name="contextcache",
    version="1.0.0",
    description="ContextCache - AI Memory Engine",
    author="Nikhil Dodda",
    packages=find_packages(),
    install_requires=[
        "typer[all]",
        "rich",
        "httpx",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "contextcache=backend.cli.main:app",
        ],
    },
    python_requires=">=3.8",
)

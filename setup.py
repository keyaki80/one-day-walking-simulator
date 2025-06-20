from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="one-day-walking-simulator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A peaceful walking simulation game for taking breaks from computer work",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/one-day-walking-simulator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "one-day=one_day:main",
        ],
    },
    keywords="game, simulation, relaxation, pygame, walking, peaceful",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/one-day-walking-simulator/issues",
        "Source": "https://github.com/yourusername/one-day-walking-simulator",
        "Documentation": "https://github.com/yourusername/one-day-walking-simulator#readme",
    },
)

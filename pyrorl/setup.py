from setuptools import setup, find_packages

# Import the README documentation
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pyrorl",
    version="1.0.1",
    author="Stanford Intelligent Systems Laboratory",
    description="An RL Environment for Wildfire Evacuation",
    url="https://sisl.github.io/PyroRL/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["numpy", "scipy", "torch", "gymnasium", "pygame", "imageio"],
    python_requires=">=3.8",
)

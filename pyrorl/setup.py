from setuptools import setup, find_packages

# Import the README documentation
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pyrorl",
    version="0.0.3",
    author='Celtics Big 3',
    author_email='clpondoc@stanford.edu',
    description='An RL OpenAI Gym Environment for Wildfire Evacuation',
    url='https://github.com/sisl/wildfire',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires = ["numpy", "scipy", "torch", "gymnasium", "pygame", "imageio"]
)

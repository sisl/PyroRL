from setuptools import setup, find_packages

setup(
    name="wildfire_evac",
    version="0.0.13",
    author='Celtics Big 3',
    author_email='clpondoc@stanford.edu',
    description='An RL OpenAI Gym Environment for Wildfire Evacuation',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires = ["numpy", "scipy", "torch", "gymnasium", "pygame"]
)

from setuptools import setup
setup(
    name='weather-app',
    version='0.0.1',
    packages=['src', 'test'],
    install_requires=[
        # Specify your package dependencies here
        'requests == 2.28.2',
        'click == 8.1.3',
        'schedule == 1.2.0'
    ],
)

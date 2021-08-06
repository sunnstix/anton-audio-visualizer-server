"""
Anton python package configuration.

Sanket Nayak <sanketn@umich.edu>
"""

from setuptools import setup

setup(
    name='anton',
    version='0.1.0',
    packages=['anton'],
    include_package_data=True,
    install_requires=[
        'Flask',
        'numpy', 
        'pyaudio', 
        'pyqtgraph', 
        'scipy==1.4.1',
    ],
    python_requires='>=3.6',
)

from setuptools import find_packages, setup

setup(
    name='q_app',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)

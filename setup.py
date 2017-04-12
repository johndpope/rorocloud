from setuptools import setup, find_packages

setup(
    name='rorocloud',
    version='0.1-dev',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click==6.7',
        'requests==2.13.0'
    ],
    entry_points='''
        [console_scripts]
        rorocloud=rorocloud.cli:cli
    ''',
)

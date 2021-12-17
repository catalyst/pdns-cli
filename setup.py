from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.readlines()

with open('README.md') as f:
    long_description = f.readlines()

setup(
        name ='pdns-cli',
        version ='1.0.0',
        author ='Catalyst IT',
        author_email ='',
        url ='https://github.com/catalyst/pdns-cli',
        description ='PowerDNS HTTPS API client',
        long_description = "This a PowerDNS HTTPS API client implementation in Python.",
        long_description_content_type ="text/markdown",
        license ='GPLv3',
        packages = [
            "pdns_cli",
            "pdns_cli.commands"
        ],
        entry_points ={
            'console_scripts': [
                'pdns = pdns_cli.pdns:main'
            ]
        },
        classifiers =[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent",
        ],
        install_requires = requirements,
        zip_safe = False
)

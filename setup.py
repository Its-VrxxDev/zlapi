from setuptools import setup, find_packages
from pathlib import Path

VERSION = '1.0.0'
DESCRIPTION = 'zlapi: Zalo API for Python'
this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.rst").read_text()

# Setting up
setup(
    name="zlapi",
    version=VERSION,
    author="Lê Quốc Việt (Vexx)",
    author_email="<vrxxdev@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/x-rst",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests', 'aenum', 'attr', 'pycryptodome', 'datetime', 'munch'],
    keywords=['python', 'zalo', 'api', 'zalo api', 'zalo chat', 'requests'],
    classifiers=[
		"Development Status :: 1 - Planning",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Natural Language :: English",
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: Implementation :: CPython",
		"Programming Language :: Python :: Implementation :: PyPy",
		"Topic :: Communications :: Chat",
		"Topic :: Internet :: WWW/HTTP",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
		"Topic :: Software Development :: Libraries",
		"Topic :: Software Development :: Libraries :: Python Modules"
    ]
)

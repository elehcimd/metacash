from setuptools import setup, find_packages

from version import __version__

# Get the long description from the README file
with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='metacash',
    version=__version__,
    author='Michele Dallachiesa',
    author_email='michele.dallachiesa@sigforge.com',
    packages=find_packages(exclude=["tests"]),
    scripts=[],
    url='https://github.com/elehcimd/metacash',
    license='MIT',
    description='Keep a close eye on your financial transactions',
    long_description=long_description,
    python_requires=">=3.6",
    install_requires=[
        "fabric",
        "jupyterlab",
        "joblib",
        "pandas",
        "numpy",
        "matplotlib",
        "pycodestyle",
        "pytest",
        "autopep8",
        "ipywidgets",
        "colorama",
        "qgrid"
    ],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],
)

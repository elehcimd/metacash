import os

from pycodestyle import StyleGuide

thisdir = os.path.dirname(os.path.abspath(__file__))
from metacash.version import __pkgname__


def test_pep8():
    report = StyleGuide(ignore=['E126', 'E501', 'E402', 'E127']).check_files(
        [thisdir + f'/../{__pkgname__}', thisdir + '/../fabfile.py', thisdir + '/../setup.py'])
    report.print_statistics()

    if report.messages:
        raise Exception("pep8")

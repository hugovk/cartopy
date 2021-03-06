# Copyright Cartopy Contributors
#
# This file is part of Cartopy and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.

from __future__ import (absolute_import, division, print_function)

from datetime import datetime
from fnmatch import fnmatch
import io
from itertools import chain
import os
import re
import subprocess

import pytest

import cartopy


# Add shebang possibility or C comment starter to the LICENSE_RE_PATTERN
SHEBANG_PATTERN = r'((\#\!.*|\/\*)\n)?'


LICENSE_TEMPLATE = """
# Copyright Cartopy Contributors
#
# This file is part of Cartopy and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
""".strip()
LICENSE_RE_PATTERN = re.escape(LICENSE_TEMPLATE)
LICENSE_RE = re.compile(SHEBANG_PATTERN + LICENSE_RE_PATTERN, re.MULTILINE)


# Guess cartopy repo directory of cartopy - realpath is used to mitigate
# against Python finding the cartopy package via a symlink.
CARTOPY_DIR = os.path.realpath(os.path.dirname(cartopy.__file__))
REPO_DIR = os.getenv('CARTOPY_GIT_DIR',
                     os.path.dirname(os.path.dirname(CARTOPY_DIR)))


class TestLicenseHeaders(object):
    @staticmethod
    def list_tracked_files():
        """
        Return a list of all the files under git.

        .. note::

            This function raises a ValueError if the repo root does
            not have a ".git" folder. If git is not installed on the system,
            or cannot be found by subprocess, an IOError may also be raised.

        """
        # Check the ".git" folder exists at the repo dir.
        if not os.path.isdir(os.path.join(REPO_DIR, '.git')):
            raise ValueError('{} is not a git repository.'.format(REPO_DIR))

        output = subprocess.check_output(['git', 'ls-tree', '-z', '-r',
                                          '--name-only', 'HEAD'],
                                         cwd=REPO_DIR)
        output = output.rstrip(b'\0').split(b'\0')
        res = [fname.decode() for fname in output]

        return res

    def test_license_headers(self):
        exclude_patterns = ('build/*',
                            'dist/*',
                            'docs/build/*',
                            'docs/source/examples/*.py',
                            'docs/source/sphinxext/*.py',
                            'lib/cartopy/examples/*.py',
                            'lib/cartopy/_version.py',
                            'versioneer.py',
                            )

        try:
            tracked_files = self.list_tracked_files()
        except ValueError as e:
            # Caught the case where this is not a git repo.
            return pytest.skip('cartopy installation did not look like a git '
                               'repo: ' + str(e))

        failed = []
        for fname in sorted(tracked_files):
            full_fname = os.path.join(REPO_DIR, fname)
            root, ext = os.path.splitext(full_fname)
            if ext in ('.py', '.pyx', '.c', '.cpp', '.h') and \
                    os.path.isfile(full_fname) and \
                    not any(fnmatch(fname, pat) for pat in exclude_patterns):

                if os.path.getsize(full_fname) == 0:
                    # Allow completely empty files (e.g. ``__init__.py``)
                    continue

                with io.open(full_fname, encoding='utf-8') as fh:
                    content = fh.read()

                if not bool(LICENSE_RE.match(content)):
                    failed.append(full_fname)

        assert failed == [], 'There were license header failures.'


class TestFutureImports(object):
    excluded = (
        '*/cartopy/examples/*.py',
        '*/docs/source/examples/*.py',
        '*/cartopy/_crs.py',   # A file created by setuptools for so loading.
        '*/cartopy/trace.py',  # Ditto.
        '*/cartopy/geodesic/_geodesic.py',
        '*/cartopy/_version.py',
    )

    future_imports_pattern = re.compile(
        r"^from __future__ import \(absolute_import,\s*division,\s*"
        r"print_function(,\s*unicode_literals)?\)$",
        flags=re.MULTILINE)

    def test_future_imports(self):
        # Tests that every single Python file includes the appropriate
        # __future__ import to enforce consistent behaviour.
        check_paths = [CARTOPY_DIR]

        failed = False
        for dirpath, _, files in chain.from_iterable(os.walk(path)
                                                     for path in check_paths):
            for fname in files:
                full_fname = os.path.join(dirpath, fname)
                if not full_fname.endswith('.py'):
                    continue
                if not os.path.isfile(full_fname):
                    continue
                if any(fnmatch(full_fname, pat) for pat in self.excluded):
                    continue

                is_empty = os.path.getsize(full_fname) == 0

                with io.open(full_fname, "r", encoding='utf-8') as fh:
                    content = fh.read()

                has_future_import = re.search(
                    self.future_imports_pattern, content) is not None

                if is_empty:
                    pass
                elif not has_future_import:
                    print('The file {} has no valid __future__ imports '
                          'and has not been excluded from the imports '
                          'test.'.format(full_fname))
                    failed = True

        if failed:
            raise ValueError('There were __future__ import check failures. '
                             'See stdout.')

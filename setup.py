#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os
import glob
try:
    import py2exe
except ImportError:
    pass
else:
    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    def isSystemDLL(pathname):
        if os.path.basename(pathname).lower() in (
                "libfreetype-6.dll", "sdl_ttf.dll", "libogg-0.dll"):
                return 0
        return origIsSystemDLL(pathname)
    py2exe.build_exe.isSystemDLL = isSystemDLL

    orig_byte_compile = py2exe.build_exe.byte_compile
    def byte_compile(*args, **kwargs):
        files = orig_byte_compile(*args, **kwargs)
        files.extend(os.path.abspath(d) for d in glob.glob("jelly/*.png"))
        files.extend(os.path.abspath(d) for d in glob.glob("jelly/*.ttf"))
        return files
    py2exe.build_exe.byte_compile = byte_compile

setup(
    name='jelly',
    version='1.0',
    author='Radomir Dopieralski',
    packages=['jelly'],
    scripts=['run_jelly.py'],
    include_package_data=True,
    zip_safe=True,
    install_requires=['distribute', 'pygame'],
    platforms='any',
    options = {
        'py2exe': {
            'bundle_files': 1,
            'packages': 'jelly',
            'compressed': True,
            'ascii': True,
            'excludes': [
                'doctest',
                'pdb',
                'unittest',
                'difflib',
                'inspect',
                'locale',
                'pyreadline',
                'optparse',
                'calendar',
                'pickle',
                'email',
                '_ssl',
            ]
        },
    },
    data_files = [
        ("jelly", glob.glob("jelly/*.png") + glob.glob("jelly/*.ttf")),
    ],
    windows = [
        {
            'script': "run_jelly.py",
            'icon_resources': [
                (0, "resources/jelly.ico"),
            ]
        }
    ],
    zipfile = None,
)

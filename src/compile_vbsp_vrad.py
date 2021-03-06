from cx_Freeze import setup, Executable
import os
import utils
import pkgutil
import shutil

shutil.rmtree('../compiler', ignore_errors=True)
shutil.rmtree('../build_BEE2/compiler', ignore_errors=True)

ico_path = os.path.join(os.getcwd(), "../bee2.ico")

if utils.WIN:
    suffix = '.exe'
elif utils.MAC:
    suffix = '_osx'
elif utils.LINUX:
    suffix = '_linux'
else:
    suffix = ''

# Unneeded packages that cx_freeze detects:
EXCLUDES = [
    'argparse',  # Used in __main__ of some modules
    'bz2',  # We aren't using this compression format (shutil, zipfile etc handle ImportError)..
    'distutils',  # Found in shutil, used if zipfile is not availible
    'doctest',  # Used in __main__ of decimal and heapq
    'optparse',  # Used in calendar.__main__
    'pprint',  # From pickle, not needed
    'textwrap',  # Used in zipfile.__main__

    # We don't localise the compiler, but utils imports the modules.
    'locale', 'gettext',

    # This isn't ever used in the compiler.
    'tkinter',

    # We aren't using the Python 2 code, for obvious reasons.
    'importlib_resources._py2',

    'win32api',
    'win32com',
    'win32wnet'

    # Imported by logging handlers which we don't use..
    'win32evtlog',
    'win32evtlogutil',
    'smtplib',
    'http',
]

# These also aren't required by logging really, but by default
# they're imported unconditionally. Check to see if it's modified first.
import logging.handlers
import logging.config

if not hasattr(logging.handlers, 'socket') and not hasattr(logging.config, 'socket'):
    EXCLUDES.append('socket')
    # Subprocess uses this in UNIX-style OSes, but not Windows.
    if utils.WIN:
        EXCLUDES += ['selectors', 'select']
if not hasattr(logging.handlers, 'pickle'):
    EXCLUDES.append('pickle')
del logging

if utils.MAC or utils.LINUX:
    EXCLUDES += ['grp', 'pwd']  # Unix authentication modules, optional

    # The only hash algorithm that's used is sha512 - random.seed()
    EXCLUDES += ['_sha1', '_sha256', '_md5']

# Include the condition sub-modules that are dynamically imported.
INCLUDES = [
    'conditions.' + module
    for loader, module, is_package in
    pkgutil.iter_modules(['conditions'])
]

bee_version = input('BEE2 Version (or blank for dev): ')

import srctools

zip_includes = [
    # Add the FGD data for us.
    (os.path.join(srctools.__path__[0], 'fgd.lzma'), 'srctools/fgd.lzma'),
]
# We need to include this version data.
try:
    import importlib_resources
    zip_includes.append(
        (
            os.path.join(importlib_resources.__path__[0], 'version.txt'),
            'importlib_resources/version.txt',
         )
    )
except ImportError:
    pass


setup(
    name='VBSP_VRAD',
    version='0.1',
    options={
        'build_exe': {
            'build_exe': '../compiler',
            'excludes': EXCLUDES,
            'includes': INCLUDES,
            # These values are added to the generated BUILD_CONSTANTS module.
            'constants': 'BEE_VERSION={ver!r}'.format(
                ver=bee_version,
            ),

            # Include all modules in the zip..
            'zip_include_packages': '*',
            'zip_exclude_packages': '',
            'zip_includes': zip_includes,
        },
    },
    description='BEE2 VBSP and VRAD compilation hooks, '
                'for modifying PeTI maps during compilation.',
    executables=[
        Executable(
            'vbsp_launch.py',
            base='Console',
            icon=ico_path,
            targetName='vbsp' + suffix,
        ),
        Executable(
            'vrad.py',
            base='Console',
            icon=ico_path,
            targetName='vrad' + suffix,
        ),

        # Generate dummy exes, so if the above are renamed they
        # error cleanly.
        Executable(
            'vbsp_vrad_orig_err.py',
            base='Console',
            icon=ico_path,
            targetName='vbsp_original' + suffix,
        ),
        Executable(
            'vbsp_vrad_orig_err.py',
            base='Console',
            icon=ico_path,
            targetName='vrad_original' + suffix,
        ),
    ]
)

# Copy the compiler to the frozen-BEE2 build location also
shutil.copytree('../compiler', '../build_BEE2/compiler')

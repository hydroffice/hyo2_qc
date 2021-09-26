import codecs
import os
import re
import numpy as np

# Always prefer setuptools over distutils
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize

# ------------------------------------------------------------------
#                         HELPER FUNCTIONS

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M, )
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")


# ------------------------------------------------------------------
#                          POPULATE SETUP

setup(
    name="hyo2.qc",
    version=find_version("hyo2", "qc", "__init__.py"),
    license="LGPLv3 license",

    namespace_packages=["hyo2"],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "*.test*", ]),
    package_data={
        "": ["media/*.png", "media/*.ico", "media/*.icns", "media/*.txt",],
    },
    zip_safe=False,
    setup_requires=[
        "setuptools",
        "wheel",
    ],
    install_requires=[
        "hyo2.abc",
        "hyo2.grids",
        "hyo2.enc",
        "matplotlib",
        "scipy",
        "pillow",
        "piexif",
        # "PySide2",
    ],
    ext_modules=cythonize([
        Extension("hyo2.qc.survey.fliers.find_fliers_checks",
                  sources=["hyo2/qc/survey/fliers/find_fliers_checks.pyx"],
                  include_dirs=[np.get_include()],
                  language='c++',
                  # extra_compile_args=["-Zi", "/Od"],
                  # extra_link_args=["-debug"],
                  ),
        Extension("hyo2.qc.survey.gridqa.grid_qa_calc",
                  sources=["hyo2/qc/survey/gridqa/grid_qa_calc.pyx"],
                  include_dirs=[np.get_include()],
                  language='c++',
                  ),
    ], annotate=True),
    python_requires='>=3.5',
    entry_points={
        "gui_scripts": [
            'qctools = hyo2.qc.qctools.gui:gui',
        ],
        "console_scripts": [
        ],
    },
    test_suite="tests",

    description="A package to quality control hydrographic data.",
    long_description="A package to quality control hydrographic data.", #(read("README.rst")),
    url="https://github.com/hydroffice/hyo2_qc",
    classifiers=[  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Office/Business :: Office Suites',
    ],
    keywords="hydrography ocean mapping survey data quality",
    author="Giuseppe Masetti(UNH,CCOM), Tyanne Faulkes(NOAA,OCS), Julia Wallace(NOAA,OCS), Matthew Wilson(NOAA,OCS)",
    author_email="gmasetti@ccom.unh.edu, tyanne.faulkes@noaa.gov, julia.wallace@noaa.gov, matthew.wilson@noaa.gov"
)

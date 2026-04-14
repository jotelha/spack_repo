# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.python import PythonPackage

from spack.package import *


class PyParmed(PythonPackage):
    """ParmEd is a general tool for aiding in investigations of
    biomolecular systems using popular molecular simulation
    packages, like Amber, CHARMM, and OpenMM written in
    Python."""

    homepage = "https://parmed.github.io/ParmEd/html/index.html"
    pypi = "ParmEd/ParmEd-3.4.3.tar.gz"

    license("MIT")

    version("3.4.3", sha256="90afb155e3ffe69230a002922b28968464126d4450059f0bd97ceca679c6627c")

    depends_on("cxx", type="build")  # generated

    depends_on("python@2.7:", type=("build", "run"))
    depends_on("py-setuptools", type="build")
    depends_on("py-six", type=("build", "run"))  # to replace the ancient bundled copy

    @run_after("install")
    def replace_bundled_six(self):
        """Replace parmed's bundled six 1.9.0 with the spack-installed six 1.17.0.

        The ancient bundled copy uses a _SixMetaPathImporter that breaks under
        Python 3.12+ (changed import-system API).  Substituting the modern six
        is safe: six is backward-compatible and all parmed.utils.six usages work
        with 1.17.0.
        """
        import glob, shutil, os

        # Locate the installed six.py from py-six's prefix
        six_candidates = glob.glob(
            join_path(self.spec["py-six"].prefix,
                      "lib", "python*", "site-packages", "six.py")
        )
        if not six_candidates:
            raise InstallError("Could not find six.py in py-six prefix")
        six_src = six_candidates[0]

        # Patch every copy of parmed/utils/six.py in the install tree
        for dst in glob.glob(
            join_path(self.prefix, "lib", "python*", "site-packages",
                      "parmed", "utils", "six.py")
        ):
            shutil.copy2(six_src, dst)

    @run_before("install")
    def patch_numpy_compat(self):
        """Fix parmed/utils/netcdf.py: numpy.compat was removed in numpy 2.0."""
        old = "from numpy.compat import asbytes, asstr"
        new = (
            "try:\n"
            "    from numpy.compat import asbytes, asstr\n"
            "except ImportError:  # numpy >= 2.0 removed numpy.compat\n"
            "    def asbytes(s): return s.encode('latin-1') if isinstance(s, str) else bytes(s)\n"
            "    def asstr(s): return s.decode('latin-1') if isinstance(s, bytes) else str(s)"
        )
        filter_file(old, new, join_path("parmed", "utils", "netcdf.py"), string=True)

    @run_before("install")
    def patch_versioneer_py3_12(self):
        """Fix versioneer.py incompatibilities with Python 3.12+:
        - SafeConfigParser removed → use RawConfigParser
        - readfp() removed → use read_file()
        """
        filter_file(
            "configparser.SafeConfigParser()",
            "configparser.RawConfigParser()",
            "versioneer.py",
            string=True,
        )
        filter_file(
            "parser.readfp(f)",
            "parser.read_file(f)",
            "versioneer.py",
            string=True,
        )

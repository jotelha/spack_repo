from spack_repo.builtin.build_systems.python import PythonPackage

from spack.package import *


class Intermol(PythonPackage):
    """InterMol: a tool for converting between molecular simulation formats."""

    homepage = "https://github.com/jotelha/InterMol"
    git      = "https://github.com/jotelha/InterMol.git"

    maintainers = ["jotelha"]

    version(
        "2026-01-28-use-gmx-mpi",
        branch="2026-01-28-use-gmx-mpi",
    )

    # --- Python ---
    depends_on("python@3.10:", type=("build", "run"))
    depends_on("py-pip", type="build")

    # REQUIRED for pyproject.toml / PEP517
    depends_on("py-setuptools", type="build")
    depends_on("py-wheel", type="build")

    # --- Python deps ---
    depends_on("py-numpy", type=("build", "run"))
    depends_on("py-parmed", type=("build", "run"))
    depends_on("py-six", type=("build", "run"))

    # --- External MD engines ---
    # gromacs and lammps are called at runtime via shell; they are loaded
    # separately as RCCS system modules, so we don't declare them as spack deps.

    # InterMol uses entry points / scripts
    install_time_test_callbacks = ["import_test"]

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

    def import_test(self):
        import intermol

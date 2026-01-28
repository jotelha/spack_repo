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
    depends_on("python@3.10", type=("build", "run"))
    depends_on("py-pip", type="build")

    # REQUIRED for pyproject.toml / PEP517
    depends_on("py-setuptools", type="build")
    depends_on("py-wheel", type="build")

    # --- Python deps ---
    depends_on("py-numpy", type=("build", "run"))
    depends_on("py-parmed", type=("build", "run"))
    depends_on("py-six", type=("build", "run"))

    # --- External MD engines ---
    depends_on("gromacs", type="run")
    depends_on("lammps", type="run")

    # InterMol uses entry points / scripts
    install_time_test_callbacks = ["import_test"]

    def import_test(self):
        import intermol

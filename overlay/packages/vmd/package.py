# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack_repo.builtin.build_systems.generic import Package

from spack.package import *


class Vmd(Package):
    """VMD provides user-editable materials which can be applied
    to molecular geometry.

    These material properties control the details of how VMD shades
    the molecular geometry, and how transparent or opaque the displayed
    molecular geometry is. With this feature, one can easily create nice
    looking transparent surfaces which allow inner structural details to
    be seen within a large molecular structure. The material controls can
    be particularly helpful when rendering molecular scenes using external
    ray tracers, each of which typically differ slightly.
    """

    homepage = "https://www.ks.uiuc.edu/Research/vmd/"
    version(
        "2.0.0a9",
        sha256="a5a13ffab0b6fa02cd294037fc40560ce8c49392431d561c2d8802df3a412b21",
        url="file://{0}/vmd-2.0.0a9.bin.LINUXAMD64.tar.gz".format(
            os.getcwd()
        ),
    )
    manual_download = True

    depends_on("libx11", type=("run", "link"))
    depends_on("libxi", type=("run", "link"))
    depends_on("libxinerama", type=("run", "link"))
    depends_on("gl@3:", type=("run", "link"))
    depends_on("patchelf", type="build")
    depends_on("gmake", type="build")

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        env.set("VMDINSTALLBINDIR", self.prefix.bin)
        env.set("VMDINSTALLLIBRARYDIR", self.prefix.lib64)

    def install(self, spec, prefix):
        configure = Executable("./configure")
        configure("LINUXAMD64")
        with working_dir(join_path(self.stage.source_path, "src")):
            make("install")

    @run_after("install")
    def ensure_rpaths(self):
        # make sure the executable finds and uses the Spack-provided
        # libraries, otherwise the executable may or may not run depending
        # on what is installed on the host
        patchelf = which("patchelf")
        rpath = ":".join(
            self.spec[dep].libs.directories[0] for dep in ["libx11", "libxi", "libxinerama", "gl"]
        )
        patchelf("--set-rpath", rpath, join_path(self.prefix, "lib64", "vmd_LINUXAMD64"))

    def setup_run_environment(self, env: EnvironmentModifications) -> None:
        env.set("PLUGINDIR", self.spec.prefix.lib64.plugins)

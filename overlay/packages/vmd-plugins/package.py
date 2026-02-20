from spack.package import *
import os
import shutil


class VmdCustomPlugins(Package):
    """Custom VMD plugin bundle layered on top of VMD 2.0.0a9"""

    homepage = "https://www.ks.uiuc.edu/Research/vmd/"

    version(
        "1.9.4a55-plugins",
        sha256="3bc9c5b27eb1434f20d17bc1b75ddf3b3ea47924a8496dcc790be8f0a47d91a4",
        url="file://{0}/vmd-1.9.4a55.bin.LINUXAMD64-CUDA102-OptiX650-OSPRay185-RTXRTRT.opengl.tar.gz".format(
            os.getcwd()
        ),
    )

    manual_download = True


    # ------------------------------------------------------------------
    # Plugin resources (pinned commits for reproducibility)
    # ------------------------------------------------------------------

    resource(
        name="topotools",
        git="https://github.com/jotelha/topotools.git",
        commit="156faf9",
    )

    resource(
        name="pbctools",
        git="https://github.com/frobnitzem/pbctools.git",
        commit="41e449e",
    )

    resource(
        name="mergetools",
        git="https://github.com/jotelha/mergetools.git",
        commit="8bca683",
    )

    # ------------------------------------------------------------------
    # Dependencies
    # ------------------------------------------------------------------

    depends_on("vmd@2.0.0a9")
    depends_on("tcl-tcllib")

    # ------------------------------------------------------------------
    # Build setup
    # ------------------------------------------------------------------

    def setup_build_environment(self, env):
        tcl = self.spec["tcl-tcllib"]
        env.set("TCLINC", f"-I{tcl.prefix.include}")
        env.set("TCLLIB", f"-L{tcl.prefix.lib}")

    # ------------------------------------------------------------------
    # Install
    # ------------------------------------------------------------------

    def install(self, spec, prefix):

        plugins_dir = os.path.join(self.stage.source_path, "plugins")

        if not os.path.isdir(plugins_dir):
            raise InstallError("Plugins directory not found in VMD bundle")

        # --------------------------------------------------------------
        # Replace bundled plugins with pinned resources
        # --------------------------------------------------------------

        for d in ["topotools", "pbctools"]:
            shutil.rmtree(os.path.join(plugins_dir, d), ignore_errors=True)

        install_tree(
            self.stage.resource_path("topotools"),
            os.path.join(plugins_dir, "topotools"),
        )

        install_tree(
            self.stage.resource_path("pbctools"),
            os.path.join(plugins_dir, "pbctools"),
        )

        install_tree(
            self.stage.resource_path("mergetools"),
            os.path.join(plugins_dir, "mergetools"),
        )

        with working_dir(plugins_dir):

            # Patch Tcl version
            filter_file("tcl8.5", "tcl8.6", recursive=True)

            # Add mergetools to build list
            makefile = os.path.join(plugins_dir, "Makefile")

            with open(makefile, "r") as f:
                lines = f.readlines()

            # Check if mergetools already listed
            if not any("mergetools" in line for line in lines):
                new_lines = []
                for line in lines:
                    if "$(MSEQBUILDDIRS)" in line:
                        new_lines.append("  mergetools \\\n")
                    new_lines.append(line)

                with open(makefile, "w") as f:
                    f.writelines(new_lines)

            make("LINUXAMD64")

            plugindir = os.path.join(prefix, "plugins")
            mkdirp(plugindir)

            env["PLUGINDIR"] = plugindir
            make("distrib")

    # ------------------------------------------------------------------
    # Runtime environment
    # ------------------------------------------------------------------

    def setup_run_environment(self, env):
        env.prepend_path(
            "VMDPLUGINPATH",
            os.path.join(self.prefix, "plugins", "LINUXAMD64")
        )
        env.prepend_path(
            "VMDPLUGINPATH",
            os.path.join(self.prefix, "plugins", "noarch")
        )

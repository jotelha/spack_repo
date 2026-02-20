from spack.package import *
import os
import shutil


class VmdPlugins(Package):
    """Custom VMD plugin bundle layered on top of VMD 2.0.0a9"""

    homepage = "https://www.ks.uiuc.edu/Research/vmd/"

    version(
        "1.9.4a57",
        sha256="de278d0c5d969336d89068e0806fb50aaa0cb0f546ba985d840b279357860679",
        url="file://{0}/vmd-1.9.4a57.src.tar.gz".format(
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
    depends_on("tcl@8.6")
    depends_on("tcl-tcllib")
    depends_on("gmake", type="build")
    # depends_on("imagemagick", type="build")
    # depends_on("latex2html", type="build")

    def patch(self):
        src = 'plugins/molfile_plugin/src/qcschemaplugin.c'
        # Ensure intptr_t is available
        filter_file(
            r'#include <stdio\.h>',
            '#include <stdio.h>\n#include <stdint.h>',
            src
        )
        # Fix pointer-to-int assignments that break under GCC 14
        filter_file(
            r'data->totalcharge = aux_value->u\.object\.values\[j\]\.value;',
            'data->totalcharge = (int)(intptr_t)aux_value->u.object.values[j].value;',
            src
        )
        filter_file(
            r'data->multiplicity = aux_value->u\.object\.values\[j\]\.value;',
            'data->multiplicity = (int)(intptr_t)aux_value->u.object.values[j].value;',
            src
        )
        # Skip autoimd doc build - requires LaTeX/ImageMagick, not needed for plugins
        filter_file(
            r'doc/ug\.pdf',
            '',
            'plugins/autoimd/Makefile'
        )
    # ------------------------------------------------------------------
    # Build setup
    # ------------------------------------------------------------------

    def setup_build_environment(self, env):
        tcl = self.spec["tcl"]
        env.set("TCLINC", f"-I{tcl.prefix.include}")
        env.set("TCLLIB", f"-L{tcl.prefix.lib}")

        # env.append_flags("CFLAGS", "-fcommon")
        # env.append_flags("CFLAGS", "-Wno-error")
        # env.append_flags("CFLAGS", "-Wno-int-conversion")

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
            os.path.join(self.stage.source_path, "topotools"),
            os.path.join(plugins_dir, "topotools"),
        )

        install_tree(
            os.path.join(self.stage.source_path, "pbctools"),
            os.path.join(plugins_dir, "pbctools"),
        )

        install_tree(
            os.path.join(self.stage.source_path, "mergetools"),
            os.path.join(plugins_dir, "mergetools"),
        )

        with working_dir(plugins_dir):

            # Patch Tcl version
            for root, _, files in os.walk(plugins_dir):
                for filename in files:
                    path = os.path.join(root, filename)

                    # Only touch regular files
                    if not os.path.isfile(path):
                        continue

                    filter_file("tcl8.5", "tcl8.6", path)

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

from conan import ConanFile
from conan.tools.files import get, copy
import os


class BasicConanfile(ConanFile):
    name = "qnn"
    description = "Qualcomm AI Engine Direct"
    license = "QTIL"

    settings = "os", "arch"

    build_policy = "missing"

    target_socs = ["68", "69", "73", "75"]

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        self.folders.build = "build"
        self.folders.generators = "build/generators"
        self.folders.imports = "build/imports"
        self.folders.package = "package"

    def package(self):

        linux = "linux"
        _arch = str(self.settings.arch).lower()
        if _arch == "armv8":
            _arch = "aarch64"
            linux = "oe-linux"
        elif _arch == "x86_64":
            linux = "linux-clang"

        _os = {"Windows": "windows-msvc", "Linux": linux, "Android": "android"}.get(
            str(self.settings.os)
        )

        include_path = os.path.join(
            self.source_folder, "qairt", str(self.version), "include"
        )

        base_lib_path = os.path.join(
            self.source_folder, "qairt", str(self.version), "lib"
        )
        lib_dir = _arch + "-" + _os

        lib_path = os.path.join(base_lib_path, lib_dir)

        copy(self, "*.h", include_path, os.path.join(self.package_folder, "include"))
        copy(
            self,
            "libQnnTFLiteDelegate.so",
            lib_path,
            os.path.join(self.package_folder, "lib", "tflite"),
        )
        copy(
            self,
            "libQnnSystem.so",
            lib_path,
            os.path.join(self.package_folder, "lib", "htp"),
        )
        copy(
            self,
            "libQnnHtp*.so",
            lib_path,
            os.path.join(self.package_folder, "lib", "htp"),
        )

        for soc in self.target_socs:
            soc_dir = os.path.join(
                self.package_folder, base_lib_path, "hexagon-v" + soc, "unsigned"
            )
            copy(
                self,
                "libQnnHtpV" + soc + "Skel.so",
                soc_dir,
                os.path.join(self.package_folder, "lib", "htp"),
            )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "qnn")
        self.cpp_info.names["cmake_find_package"] = "qnn"
        self.cpp_info.names["cmake_find_package_multi"] = "qnn"
        self.cpp_info.set_property("cmake_target_name", "qnn::qnn")

        self.cpp_info.components["tfliteDelegate"].libs = ["QnnTFLiteDelegate"]
        self.cpp_info.components["tfliteDelegate"].libdirs = ["lib/tflite"]
        self.cpp_info.components["tfliteDelegate"].set_property(
            "cmake_target_name", "qnn::tfliteDelegate"
        )

        htp_libs = ["QnnSystem", "QnnHtp", "QnnHtpPrepare"]

        for soc in self.target_socs:
            htp_libs += ["QnnHtpV" + soc + "Stub", "QnnHtpV" + soc + "Skel"]

        self.cpp_info.components["htp"].libs = htp_libs
        self.cpp_info.components["htp"].libdirs = ["lib/htp"]
        self.cpp_info.components["htp"].set_property("cmake_target_name", "qnn::htp")

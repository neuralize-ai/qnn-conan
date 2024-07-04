from conan import ConanFile
from conan.tools.files import get, copy
import os


class BasicConanfile(ConanFile):
    name = "qnn"
    version = "2.22.0.240425"
    description = "Qualcomm AI Engine Direct"
    license = "QTIL"

    settings = "os", "arch"

    build_policy = "missing"

    no_copy_source = True

    target_socs = ["68", "69", "73", "75"]

    def source(self):
        qnn_url = (
            "https://softwarecenter.qualcomm.com/api/download/software/qualcomm_neural_processing_sdk/v"
            + self.version
            + ".zip"
        )
        qnn_checksum = (
            "d68ed4d92187101a9759384cbce0a35bd383840b2e3c3c746a4d35f99823a75a"
        )
        get(self, qnn_url, sha256=qnn_checksum)

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

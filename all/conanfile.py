from conan import ConanFile
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration
import os


class BasicConanfile(ConanFile):
    name = "qnn"
    description = "Qualcomm AI Engine Direct"
    license = "QTIL"

    settings = "os", "arch"

    options = {
        "with_tflite": [True, False],
    }

    default_options = {
        "with_tflite": True,
    }

    package_type = "shared-library"

    target_socs = ["68", "69", "73", "75"]

    def source(self):
        if self.version == "custom":
            sdk_path = os.getenv("QNN_SDK_PATH")
            if not sdk_path:
                raise ConanInvalidConfiguration(
                    "QNN_SDK_PATH environment variable is not set")
            self.output.info(f"Using QNN SDK from: {sdk_path}")
            # Copy the SDK files to the source folder
            copy(self, "*", src=sdk_path,
                 dst=os.path.join(self.source_folder, "qairt", "custom"))
        else:
            get(
                self,
                **self.conan_data["sources"][self.version],
            )

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

        source_path = os.path.join(self.source_folder, "qairt")
        source_path = os.path.join(source_path, os.listdir(source_path)[0])

        include_path = os.path.join(source_path, "include/QNN")

        base_lib_path = os.path.join(source_path, "lib")
        lib_dir = _arch + "-" + _os

        lib_path = os.path.join(base_lib_path, lib_dir)

        copy(self, "*.h", include_path,
             os.path.join(self.package_folder, "include"))

        copy(
            self,
            "libQnnTFLiteDelegate.so",
            lib_path,
            os.path.join(self.package_folder, "lib", "tflite"),
        )

        htp_prepare_lib = (
            "HtpPrepare" if self.settings.arch == "x86_64" else "QnnHtpPrepare"
        )

        htp_libs = ["QnnSystem", "QnnHtp", htp_prepare_lib]

        for htpLib in htp_libs:
            libName = "lib" + htpLib + ".so"
            copy(
                self,
                libName,
                lib_path,
                os.path.join(self.package_folder, "lib", "htp"),
            )

        if self.settings.arch == "armv8":
            for soc in self.target_socs:
                stubLib = "libQnnHtpV" + soc + "Stub.so"
                skelLib = "libQnnHtpV" + soc + "Skel.so"

                copy(
                    self,
                    stubLib,
                    lib_path,
                    os.path.join(self.package_folder, "lib", "htp"),
                )

                soc_dir = os.path.join(
                    self.package_folder, base_lib_path, "hexagon-v" + soc, "unsigned"
                )
                copy(
                    self,
                    skelLib,
                    soc_dir,
                    os.path.join(self.package_folder, "lib", "htp"),
                )

    def package_info(self):
        self.cpp_info.components["headers"].set_property(
            "cmake_target_name", "qnn::headers"
        )
        self.cpp_info.components["headers"].includedirs = ["include"]
        self.cpp_info.components["headers"].libs = []
        self.cpp_info.components["headers"].libdirs = []

        if self.options.with_tflite and self.settings.os == "Android":
            self.cpp_info.components["tflite"].set_property(
                "cmake_target_name", "qnn::tflite"
            )
            self.cpp_info.components["tflite"].libs = ["QnnTFLiteDelegate"]
            self.cpp_info.components["tflite"].libdirs = ["lib/tflite"]

        if self.settings.arch == "armv8":
            self.cpp_info.components["htp"].set_property(
                "cmake_target_name", "qnn::htp"
            )
            self.cpp_info.components["htp"].libdirs = ["lib/htp"]

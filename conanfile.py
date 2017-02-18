from conans import ConanFile, CMake, ConfigureEnvironment, tools
import os
from os import path
import shutil

class KademliaConan(ConanFile):
    name        = "kademlia"
    version     = "0.0.1-3f7a0a5"
    repo_url    = "https://github.com/DavidKeller/kademlia"
    settings    = "os", "compiler", "arch"
    generators  = "cmake"
    exports     = ("CMakeLists.txt",)

    options     = {
        "shared": [True, False]
    }
    default_options = (
        "shared=False"
    )

    requires = (
        "Boost/1.59.0@lasote/stable",
        "OpenSSL/1.0.2j@lasote/stable",
        
        "cmake_installer/0.1@lasote/testing"
    )

    commit = "3f7a0a5"
    git_dirname = name

    def source(self):
        # Clone the repository
        self.run("git clone %s %s" % (self.repo_url, self.git_dirname))
        self.run("git checkout %s" % self.commit, cwd=self.git_dirname)

        main_cmakelists = path.join(self.git_dirname, "CMakeLists.txt")
        shutil.move(main_cmakelists, path.join(self.git_dirname, "CMakeListsOriginal.cmake"))
        shutil.move("CMakeLists.txt", main_cmakelists)
        
    def build(self):
        #Make build dir
        self.build_dir = self.try_make_dir(os.path.join(".", "build"))

        cmake = CMake(self.settings)
        env = ConfigureEnvironment(self)
        
        self.cmake_configure(cmake, env, self.build_dir)
        self.cmake_build_and_install(cmake, env, self.build_dir)
        
    def package(self):
        include_dir = path.join(self.git_dirname, "include")
        self.copy("**.h"  , src=include_dir, dst="include", keep_path=True)
        self.copy("**.hpp", src=include_dir, dst="include", keep_path=True)
        
        # Copy libs
        src_bin = path.join(self.build_dir, "bin")
        src_lib = path.join(self.build_dir, "lib")
        
        if self.options.shared:
            self.copy("*.dll"  , dst="bin", src=src_bin, keep_path=False)
            self.copy("*.so*"  , dst="lib", src=src_lib, keep_path=False)
            self.copy("*.dylib", dst="lib", src=src_lib, keep_path=False)
        else:
            self.copy("*.lib", dst="lib", src=src_lib, keep_path=False)
            self.copy("*.a"  , dst="lib", src=src_lib, keep_path=False)
            

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs      = ["kademlia"]
        else:
            self.cpp_info.libs      = ["kademlia_static"]
            

####################################### Helpers ################################################

    def cmake_configure(self, cmake, env, build_dir):    
        src_dir = path.join(self.conanfile_directory, self.git_dirname)
        
        cmake_cmd = 'cmake "%s" %s %s' % (src_dir, cmake.command_line, self.cmake_args())
        
        self.output.info(cmake_cmd)
        self.run(env.command_line + " " + cmake_cmd, cwd=build_dir)
        
    def cmake_build_and_install(self, cmake, env, build_dir):
        self.run('%s cmake --build . %s' % (env.command_line, cmake.build_config), cwd=build_dir)
        
    def cmake_args(self):
        """Generate arguments for cmake"""

        if not hasattr(self, 'package_folder'):
            self.package_folder = "dist"

        args = [
        ]
        args += [
            '-DCMAKE_INSTALL_PREFIX="%s"' % self.package_folder
        ]
        
        if not self.options["Boost"].shared:
            self.output.info("static boost!")
            args.append("-DBoost_USE_STATIC_LIBS=ON")
        else:
            self.output.info("shared boost!")
            

        return ' '.join(args)

    def cmake_bool_option(self, name, value):
        return "-D%s=%s" % (name.upper(), "ON" if value else "OFF");

    def try_make_dir(self, dir):
        try:
            os.mkdir(dir)
        except OSError:
            #dir already exist
            pass

        return dir

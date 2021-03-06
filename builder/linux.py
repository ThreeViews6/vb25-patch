#
# V-Ray/Blender Build System
#
# http://vray.cgdo.ru
#
# Author: Andrey M. Izrantsev (aka bdancer)
# E-Mail: izrantsev@cgdo.ru
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.
#


import os
import sys
import shutil
import subprocess

from .builder import utils
from .builder import Builder


Deps = {
	'ubuntu': {
		'cmd' : "apt-get install",
		'packages' : (
			'build-essential',
			'libalut-dev',
			'libavcodec-dev',
			'libavdevice-dev',
			'libavformat-dev',
			'libavutil-dev',
			'libfftw3-dev',
			'libfreetype6-dev',
			'libglew-dev',
			'libcheese-dev', # Fixes libglew-dev installation
			'libglu1-mesa-dev',
			'libjack-dev',
			'libjack-dev',
			'libjpeg-dev',
			'libmp3lame-dev',
			'libopenal-dev',
			'libopenexr-dev',
			'libopenjpeg-dev',
			'libpng12-dev',
			'libsdl1.2-dev',
			'libsndfile1-dev',
			'libspnav-dev',
			'libswscale-dev',
			'libtheora-dev',
			'libtiff4-dev',
			'libvorbis-dev',
			'libx264-dev',
			'libxi-dev',
			'python3.4-dev',
			'python3-numpy',
			'libopenimageio-dev',
			'libopencolorio-dev',
			'libboost-all-dev'
		)
	},
}


def DepsInstall(self):
	sys.stdout.write("Installing dependencies: \n")

	distr = utils.get_linux_distribution()['short_name']

	if distr in Deps:
		cmd = "sudo %s %s" % (
			Deps[distr]['cmd'],
			" ".join(Deps[distr]['packages'])
		)
		sys.stdout.write("Calling: %s\n" % cmd)
		os.system(cmd)

	else:
		sys.stdout.write("Your distribution \"%s\" doesn't support automatic dependencies installation!\n" % distr)


def DepsBuild(self):
	cmd = "sudo -E %s/install_deps.sh --source %s --install /opt" % (
		utils.path_join(self.dir_source, 'vb25-patch'),
		utils.path_join(self.dir_source, "blender-deps")
	)

	if not self.with_osl:
		cmd += " --skip-llvm"
		cmd += " --skip-osl"

	if self.with_collada:
		cmd += " --with-opencollada"
	else:
		cmd += " --skip-opencollada"

	if self.mode_test:
		sys.stdout.write(cmd)
		sys.stdout.write("\n")
	else:
		os.system(cmd)


class LinuxBuilder(Builder):
	def post_init(self):
		pass

	def compile(self):
		cmake_build_dir = os.path.join(self.dir_source, "blender-cmake-build")
		if not os.path.exists(cmake_build_dir):
			os.makedirs(cmake_build_dir)
		os.chdir(cmake_build_dir)

		cmake = ['cmake']

		cmake.append("-G")
		cmake.append("Ninja")

		cmake.append("-DWITH_VRAY_FOR_BLENDER=ON")
		cmake.append("-DCMAKE_BUILD_TYPE=%s" % self.build_type.capitalize())
		cmake.append('-DCMAKE_INSTALL_PREFIX=%s' % self.dir_install_path)

		if self.dev_static_libs:
			cmake.append("-DBoost_DIR=/opt/boost")
			cmake.append("-DBoost_INCLUDE_DIR=/opt/boost/include")
			cmake.append("-DBoost_LIBRARY_DIRS=/opt/boost/lib")
			cmake.append("-DBoost_DATE_TIME_LIBRARY=/opt/boost/lib/libboost_date_time.a")
			cmake.append("-DBoost_DATE_TIME_LIBRARY_DEBUG=/opt/boost/lib/libboost_date_time.a")
			cmake.append("-DBoost_DATE_TIME_LIBRARY_RELEASE=/opt/boost/lib/libboost_date_time.a")
			cmake.append("-DBoost_FILESYSTEM_LIBRARY=/opt/boost/lib/libboost_filesystem.a")
			cmake.append("-DBoost_FILESYSTEM_LIBRARY_DEBUG=/opt/boost/lib/libboost_filesystem.a")
			cmake.append("-DBoost_FILESYSTEM_LIBRARY_RELEASE=/opt/boost/lib/libboost_filesystem.a")
			cmake.append("-DBoost_REGEX_LIBRARY=/opt/boost/lib/libboost_regex.a")
			cmake.append("-DBoost_REGEX_LIBRARY_DEBUG=/opt/boost/lib/libboost_regex.a")
			cmake.append("-DBoost_REGEX_LIBRARY_RELEASE=/opt/boost/lib/libboost_regex.a")
			cmake.append("-DBoost_SYSTEM_LIBRARY=/opt/boost/lib/libboost_system.a")
			cmake.append("-DBoost_SYSTEM_LIBRARY_DEBUG=/opt/boost/lib/libboost_system.a")
			cmake.append("-DBoost_SYSTEM_LIBRARY_RELEASE=/opt/boost/lib/libboost_system.a")
			cmake.append("-DBoost_THREAD_LIBRARY=/opt/boost/lib/libboost_thread.a")
			cmake.append("-DBoost_THREAD_LIBRARY_DEBUG=/opt/boost/lib/libboost_thread.a")
			cmake.append("-DBoost_THREAD_LIBRARY_RELEASE=/opt/boost/lib/libboost_thread.a")
			cmake.append("-DBoost_LOCALE_LIBRARY=/opt/boost/lib/libboost_locale.a")
			cmake.append("-DBoost_LOCALE_LIBRARY_DEBUG=/opt/boost/lib/libboost_locale.a")
			cmake.append("-DBoost_LOCALE_LIBRARY_RELEASE=/opt/boost/lib/libboost_locale.a")
			cmake.append("-DOPENEXR_ROOT_DIR=/opt/openexr")
			cmake.append("-DOPENEXR_ILMIMF_LIBRARY=/opt/openexr/lib/libIlmImf-2_1.a")
			cmake.append("-D_opencolorio_LIBRARIES=/opt/ocio/lib/libOpenColorIO.a")
			cmake.append("-DOPENCOLORIO_INCLUDE_DIR=/opt/ocio/include")
			cmake.append("-DOPENCOLORIO_TINYXML_LIBRARY=/opt/ocio/lib/libtinyxml.a")
			cmake.append("-DOPENCOLORIO_YAML-CPP_LIBRARY=/opt/ocio/lib/libyaml-cpp.a")
			cmake.append("-DOPENIMAGEIO_INCLUDE_DIR=/opt/oiio/include/")
			cmake.append("-DOPENIMAGEIO_LIBRARY=/opt/oiio/lib/libOpenImageIO.a")
			cmake.append("-DPYTHON_VERSION=3.4")
			cmake.append("-DPYTHON_ROOT_DIR=/opt/python-3.3")
			cmake.append("-DPYTHON_LIBRARY=/opt/python-3.3/lib/libpython3.4m.a")
			cmake.append("-DPYTHON_LIBPATH=/opt/python-3.3/lib")
			cmake.append("-DPYTHON_LIBRARIES=/opt/python-3.3/lib")
			cmake.append("-DPYTHON_INCLUDE_DIR=/opt/python-3.3/include/python3.4m")
			cmake.append("-DPYTHON_INCLUDE_CONFIG_DIR=/opt/python-3.3/include/python3.4m")
			cmake.append("-DPYTHON_NUMPY_PATH=/opt/python-3.3/lib/python3.4/site-packages")

		cmake.append("-DWITH_GAMEENGINE=%s" % utils.GetCmakeOnOff(self.with_ge))
		cmake.append("-DWITH_PLAYER=%s" % utils.GetCmakeOnOff(self.with_player))
		cmake.append("-DWITH_LIBMV=%s" % utils.GetCmakeOnOff(self.with_tracker))
		cmake.append("-DWITH_OPENCOLLADA=%s" % utils.GetCmakeOnOff(self.with_collada))
		cmake.append("-DWITH_MOD_OCEANSIM=ON")
		cmake.append("-DWITH_FFTW3=ON")

		cmake.append("../blender")

		if self.mode_test:
			print(" ".join(cmake))

		else:
			res = subprocess.call(cmake)
			if not res == 0:
				sys.stderr.write("There was an error during configuration!\n")
				sys.exit(1)

			make = ['ninja']
			make.append('-j%s' % self.build_jobs)
			make.append('install')

			res = subprocess.call(make)
			if not res == 0:
				sys.stderr.write("There was an error during the compilation!\n")
				sys.exit(1)


	def package(self):
		subdir = "linux" + "/" + self.build_arch

		release_path = os.path.join(self.dir_release, subdir)

		if not self.mode_test:
			utils.path_create(release_path)

		archive_name = utils.GetPackageName(self)
		archive_path = utils.path_join(release_path, archive_name)

		sys.stdout.write("Generating archive: %s\n" % (archive_name))
		sys.stdout.write("  in: %s\n" % (release_path))

		cmd = "tar jcf %s %s" % (archive_path, self.dir_install_name)

		sys.stdout.write("Calling: %s\n" % (cmd))
		sys.stdout.write("  in: %s\n" % (self.dir_install))

		if not self.mode_test:
			os.chdir(self.dir_install)
			os.system(cmd)

		return subdir, archive_path

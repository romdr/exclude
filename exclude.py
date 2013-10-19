#!/usr/bin/env python
#
# exclude - C++ unused includes removal tool
# Romain Dura | romain@shazbits.com
# https://github.com/shazbits/exclude
#
# Copyright (c) 2013, Romain Dura romain@shazbits.com
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#

import os
import sys
import argparse
import subprocess

devenv_path = '"C:\\Program Files (x86)\\Microsoft Visual Studio 10.0\\Common7\\IDE\\devenv.com"'
msbuild_path = '"C:\\Windows\\Microsoft.NET\\Framework\\v4.0.30319\\msbuild"'
msbuild_options = '/t:BuildGenerateSources /t:BuildCompile /p:VisualStudioVersion=10.0 /maxcpucount:11 /nologo'

def get_includes_and_buffer_from_file(file_path, file_name):
	includes = []
	file_buffer = ''
	with open(file_path) as f:
		for line in f.readlines():
			file_buffer += line
			if line.startswith('#include') and line.find('PCH.h') == -1 and line.find(file_name.replace('.cpp', '.h')) == -1:
				includes.append(line[:-1])

	if safe_mode:
		includes = filter_out_used_include_names(includes, file_buffer)
	return includes, file_buffer

def filter_out_used_include_names(includes, file_buffer):
	filtered_includes = list(includes)
	file_lines = file_buffer.split('\n')
	for include in includes:
		include_name = include.split('/')[-1].split('.h')[0]
		#print 'Trying to exclude %s' % include_name

		for line in file_lines:
			if not line.startswith('#include') and line.find(include_name) != -1:
				filtered_includes.remove(include)
				#print 'Excluding %s because it seems used in the file' % include
				break
	return filtered_includes

def remove_include_from_file(include_line, file_buffer, file_path):
	buffer_to_write = file_buffer.replace(include_line + '\n', '')
	write_to_file(file_path, buffer_to_write)
	return buffer_to_write

def write_to_file(file_path, file_buffer):
	with open(file_path, 'w') as f:
		f.write(file_buffer)

def run(project_folder, use_msbuild, safe_mode, project_config, project_platform, project_path, solution_path, build_config, build_project, single_file_to_check):
	removed_includes = {}

	# For each file in the current project
	for root, folders, files in os.walk(project_folder):
		for file_name in files:
			# TODO: move this outside this loop and special case for the single_file_to_check option
			if single_file_to_check is not None and file_name != single_file_to_check:
				continue

			file_path = os.path.join(root, file_name)
			print '\n' + file_path

			includes, file_buffer = get_includes_and_buffer_from_file(file_path, file_name)

			# For each include in the current file
			for include in includes:
				print 'Trying to remove %s' % (include)
				sys.stdout.flush()

				new_buffer = remove_include_from_file(include, file_buffer, file_path)

				if use_msbuild:
					ret_val = subprocess.call(msbuild_path + ' %s /p:Configuration=%s /p:Platform=%s "%s" > NUL' % (msbuild_options, project_config, project_platform, project_path), shell=True)
				else:
					ret_val = subprocess.call(devenv_path + ' "%s" /build "%s" /project "%s" > NUL' % (solution_path, build_config, build_project), shell=True)

				if ret_val == 0:
					file_buffer = new_buffer

					# Keep track of what we have removed
					print '  > Removed %s' % (include)
					sys.stdout.flush()

					if file_path in removed_includes:
						removed_includes[file_path].append(include)
					else:
						removed_includes[file_path] = [include]
				else:
					write_to_file(file_path, file_buffer)

			# Print summary for this file
			if len(removed_includes.keys()) != 0:
				for file_name, includes in removed_includes.iteritems():
					print '\nRemoved includes in %s' % (file_name)
					for include in includes:
						print include
			else:
				print 'All includes ok for %s' % (file_name)

if __name__ == '__main__':
	epilog = '''
msbuild example:
exclude.py "D:\\path\\to\\code" -pc "Release" -pp "Win32" -pa "D:\\path\\to\\code\\foo\\foo.vcxproj"

devenv example:
exclude.py "D:\\path\\to\\code" -d -sp "D:\\path\\to\\code\\my.sln" -bc "Release|Win32" -bp "Foo" '''

	parser = argparse.ArgumentParser(description='Unused includes removal tool', epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('projectcodepath', help='Path to the project\'s code')
	parser.add_argument('-d', '--devenv', help='Uses devenv instead of msbuild if specified', action='store_true')
	parser.add_argument('-u', '--unsafe', help='Do not keep includes whose name is referenced in code', action='store_true')
	parser.add_argument('-pc', '--projectconfig', help='Project configuration, must be specified if using msbuild')
	parser.add_argument('-pp', '--projectplatform', help='Project platform, must be specified if using msbuild')
	parser.add_argument('-pa', '--projectpath', help='Path to vcxproj, must be specified if using msbuild')
	parser.add_argument('-sp', '--solutionpath', help='Path to sln, must be specified if using devenv')
	parser.add_argument('-bc', '--buildconfig', help='Build configuration, must be specified if using devenv')
	parser.add_argument('-bp', '--buildproject', help='Build project, must be specified if using devenv')
	parser.add_argument('-f', '--file', help='Run only on the specified file')
	args = parser.parse_args()

	project_folder = args.projectcodepath
	use_msbuild = not args.devenv
	safe_mode = not args.unsafe

	# ms build
	project_config = args.projectconfig
	project_platform = args.projectplatform
	project_path = args.projectpath

	# devenv
	solution_path = args.solutionpath
	build_config = args.buildconfig
	build_project = args.buildproject

	single_file_to_check = args.file

	run(project_folder=project_folder, use_msbuild=use_msbuild, safe_mode=safe_mode,
		project_config=project_config, project_platform=project_platform, project_path=project_path,
		solution_path=solution_path, build_config=build_config, build_project=build_project,
		single_file_to_check=single_file_to_check)

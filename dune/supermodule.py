# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 16:14:20 2012

@author: r_milk01

supermodule.py (c) 2012 rene.milk@uni-muenster.de

It is licensed to you under the terms of the WTFPLv2.
"""

import git
import os
import random
import string
import tempfile
import control
import subprocess
import shutil
import pprint
import copy
import logging

CFG_TPL = u'''#This file is intended for use on buildbot, do NOT set any compiler here
CONFIGURE_FLAGS="CXXFLAGS='-pedantic -DDEBUG -g3 -ggdb -O0 -std=c++0x -Wextra -Wall' \\
    --enable-fieldvector-size-is-method \\
    --disable-documentation "
'''

DOCS_TPL = u'''#This file is intended for use on buildbot
CONFIGURE_FLAGS="CXXFLAGS='-w -O0' \\
    --enable-fieldvector-size-is-method \\
    --enable-documentation "
'''

def generate(module_url, module_name, new_dir):
    temporary_name = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(15))
    temporary_dir = os.path.join(tempfile.gettempdir(), temporary_name)

    url_tpl = 'http://users.dune-project.org/repositories/projects/%s.git'
    git.Repo.clone_from(module_url,
                        to_path=os.path.join(temporary_dir, module_name))
    common_path = os.path.join(temporary_dir, 'dune-common')
    git.Repo.clone_from(url_tpl % 'dune-common',
                        to_path=common_path)
    ctrl_path = os.path.join(temporary_dir, 'dune-common', 'bin', 'dunecontrol')
    ctrl = control.Dunecontrol(ctrl_path)

    git.Repo.init(new_dir)
    m_deps = ctrl.dependencies(module_name)
    deps = copy.deepcopy(m_deps)
    os.chdir(new_dir)

    def add_sub(dep, url=None):
        url = url or url_tpl % dep
        try:
            subprocess.check_output(['git', 'submodule', 'add', url, dep],
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            if e.output.find('already exists') < 0:
                raise e

    add_sub(module_name, module_url)
    for dep in m_deps['required'] + m_deps['suggested']:
        add_sub(dep)
    ctrl_path = os.path.join(new_dir, 'dune-common', 'bin', 'dunecontrol')
    ctrl = control.Dunecontrol(ctrl_path)
    def add_recursive(dep, cat):
        try:
            return ctrl.dependencies(dep)[cat]
        except control.ModuleMissing, m:
            add_sub(m.name)
            return add_recursive(dep,cat)
    for cat in ['required', 'suggested']:
        for dep in m_deps[cat]:
            deps[cat] = list(set(deps[cat] + add_recursive(dep,cat)))

    for dep in deps['suggested'] + deps['required']:
        add_sub(dep)

    for compiler in ['gcc-4.4', 'gcc-4.6', 'clang']:
        open(os.path.join(new_dir, 'config.opts.%s' % compiler),
             'wb').write(CFG_TPL)
    open(os.path.join(new_dir, 'config.opts.docs'), 'wb').write(DOCS_TPL)
    subprocess.check_output(['git', 'add', 'config*'],
                            stderr=subprocess.STDOUT)
    subprocess.check_output(['git', 'commit', '-m', 'intial commit'],
                            stderr=subprocess.STDOUT)
    shutil.rmtree(temporary_dir)

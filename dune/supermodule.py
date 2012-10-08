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
import copy
import logging
from collections import defaultdict

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
    url_tpl = 'http://users.dune-project.org/repositories/projects/%s.git'
    if not os.path.isdir(new_dir):
        os.makedirs(new_dir)
    git.Repo.init(new_dir)
    os.chdir(new_dir)

    def add_sub(dep, url=None):
        if dep == module_name:
            url = module_url
        else:
            url = url or url_tpl % dep
        try:
            subprocess.check_output(['git', 'submodule', 'add', url, dep],
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            logging.info(e.output)
            logging.error(e)

    add_sub('dune-common', url_tpl % 'dune-common')
    add_sub(module_name, module_url)

    ctrl = control.Dunecontrol.from_basedir(new_dir)

    def add_recursive(dep, cat):
        try:
            return ctrl.dependencies(dep)[cat]
        except control.ModuleMissing, m:
            if m.name == dep:
                logging.critical('FUBAR')
                return []
            logging.info('Recursing for %s' % m.name)
            add_sub(m.name)
            return add_recursive(dep,cat)

    deps = defaultdict(list)
    import pprint
    for cat in ['required', 'suggested']:
        deps[cat] = add_recursive(module_name, cat)
        logging.info(pprint.pformat(deps))
    for dep in deps['suggested'] + deps['required']:
        add_recursive(dep, 'required')

    for compiler in ['gcc-4.4', 'gcc-4.6', 'clang']:
        open(os.path.join(new_dir, 'config.opts.%s' % compiler),
             'wb').write(CFG_TPL)
    open(os.path.join(new_dir, 'config.opts.docs'), 'wb').write(DOCS_TPL)

    subprocess.check_output(['git', 'add', 'config*'],
                            stderr=subprocess.STDOUT)
    subprocess.check_output(['git', 'commit', '-m', 'intial commit'],
                            stderr=subprocess.STDOUT)

def get_dune_stuff():
    temporary_name = ''.join(random.choice(string.ascii_letters
                                + string.digits) for x in range(15))
    temporary_dir = os.path.join(tempfile.gettempdir(),
                                 temporary_name)
    url = 'http://users.dune-project.org/repositories/projects/dune-stuff.git'
    module = 'dune-stuff'
    generate(url, module, temporary_dir)
    return temporary_dir

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
    deps =  ctrl.dependencies(module_name)['required'] \
            + ctrl.dependencies(module_name)['suggested']
    os.chdir(new_dir)
    def add_sub(dep, url=None):
        url = url or url_tpl % dep
        subprocess.check_call(['git', 'submodule', 'add', url, dep])
    for dep in set(deps):
        add_sub(dep)
    add_sub(module_name, module_url)

    shutil.rmtree(temporary_dir)

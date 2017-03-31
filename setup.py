# Copyright 2017, IBM US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

setup(
    name='opsmgr-core',
    version='0.1',

    description='Operational Manager Core',

    author='',
    author_email='',

    url='',

    classifiers=[
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 ],

    install_requires = [
        'pbr>=2.0',
        'paramiko>=1.16.0',
        'sqlalchemy>=1.0.12',
        'stevedore>=1.12.0',
        'pyyaml>=3.11',
        'enum-compat>=0.0.2',
        'configparser>=3.5.0b2',
    ],

    platforms=['Any'],

    scripts=[],

    namespace_packages=['opsmgr'],

    provides=['opsmgr'],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'opsmgr = opsmgr.scripts.cli:main',
            'opsmgr-admin = opsmgr.scripts.cli_admin:main',
         ],
        'opsmgr.discovery.interfaces.IDiscoveryPlugin': [],
        'opsmgr.inventory.interfaces.IManagerDevicePlugin': [],
        'opsmgr.inventory.interfaces.IManagerDeviceHook': [],
        'opsmgr.inventory.interfaces.IManagerRackHook': [],
        'opsmgr.inventory.interfaces.IOperationsPlugin': [],
    },

    data_files=[('etc', ['etc/logging.yaml'])],

    zip_safe=False,
)

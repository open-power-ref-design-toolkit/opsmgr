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
        'opsmgr.inventory.interfaces.IManagerDevicePlugin': [],
        'opsmgr.inventory.interfaces.IManagerDeviceHook': [],
        'opsmgr.inventory.interfaces.IManagerRackHook': [],
    },

    data_files=[('etc', ['etc/logging.yaml'])],

    zip_safe=False,
)

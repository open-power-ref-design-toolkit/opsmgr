from setuptools import setup, find_packages

setup(
    name='opsmgr-core',
    version='0.1',

    description='Operational Manager Core',

    author='',
    author_email='',

    url='',

    classifiers=[
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 ],

    platforms=['Any'],

    scripts=[],

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

    zip_safe=False,
)

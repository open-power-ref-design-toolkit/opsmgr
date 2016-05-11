from setuptools import setup, find_packages

setup(
    name='opsmgr-plugins-operations-nagios',
    version='0.1',

    description='Operational Management Operations Plugin for Nagios',

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

    platforms=['Any'],

    scripts=[],

    namespace_packages=['opsmgr','opsmgr.plugins','opsmgr.plugins.operations'],

    provides=['opsmgr.plugins.operations.nagios'],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'opsmgr.inventory.interfaces.IManagerDeviceHook': [
            'Nagios = opsmgr.plugins.operations.nagios.NagiosOperationsPlugin:NagiosPlugin',
        ],
    },

    zip_safe=False,
)


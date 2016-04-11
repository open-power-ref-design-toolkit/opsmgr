from setuptools import setup, find_packages

setup(
    name='opsmgr-plugins-devices-mellanox',
    version='0.1',

    description='Operational Manager Device Plugin for Mellanox Ethernet Switches',

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

    namespace_packages=['opsmgr','opsmgr.plugins','opsmgr.plugins.devices'],

    provides=['opsmgr.plugins.devices.mellanox'],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'opsmgr.inventory.interfaces.IManagerDevicePlugin': [
            'MLNX-OS = opsmgr.plugins.devices.mellanox.MLNXOSManagerPlugin:MLNXOSPlugin',
        ],
    },

    zip_safe=False,
)

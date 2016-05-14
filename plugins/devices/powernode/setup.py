from setuptools import setup, find_packages

setup(
    name='opsmgr-plugins-devices-powernode',
    version='0.1',

    description='Operational Manager Device Plugin for the IBM Power Physical System',

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

    provides=['opsmgr.plugins.devices.powernode'],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'opsmgr.inventory.interfaces.IManagerDevicePlugin': [
            'PowerNode = opsmgr.plugins.devices.powernode.PowerNodePlugin:PowerNodePlugin',
        ],
    },
    zip_safe=False,
)



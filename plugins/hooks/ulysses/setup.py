from setuptools import setup, find_packages

setup(
    name='opsmgr-plugins-hooks-ulysses',
    version='0.1',

    description='Operational Management Hooks for Ulysses',

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

    namespace_packages=['opsmgr','opsmgr.plugins','opsmgr.plugins.hooks'],

    provides=['opsmgr.plugins.hooks.ulysses'],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'opsmgr.inventory.interfaces.IManagerDeviceHook': [
            'UlyssesDevice = opsmgr.plugins.hooks.ulysses.UlyssesDevicePlugin:UlyssesDevicePlugin',
        ],
    },

    zip_safe=False,
)

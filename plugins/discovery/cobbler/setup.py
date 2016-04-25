from setuptools import setup, find_packages

setup(
    name='opsmgr-plugins-discovery-cobbler',
    version='0.1',

    description='Operational Management Discovery Plugin for Cobbler',

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

    namespace_packages=['opsmgr','opsmgr.plugins','opsmgr.plugins.discovery'],

    provides=['opsmgr.plugins.discovery.cobbler'],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'opsmgr.discovery.interfaces.IDiscoveryPlugin': [
            'Cobbler = opsmgr.plugins.discovery.cobbler.CobblerDiscoveryPlugin:CobblerPlugin',
        ],
    },

    zip_safe=False,
)

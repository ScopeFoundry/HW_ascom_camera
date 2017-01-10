from setuptools import setup

setup(
    name = 'ScopeFoundryHW.ascom_camera',
    
    version = '0.0.1.dev1',
    
    description = 'ASCOM camera hardware plugin for ScopeFoundry',
    
    # Author details
    author='Edward S. Barnard',
    author_email='esbarnard@lbl.gov',

    # Choose your license
    license='MIT',

    package_dir={'ScopeFoundryHW.ascom_camera': '.'},
    
    packages=['ScopeFoundryHW.ascom_camera',],
    
    #packages=find_packages('.', exclude=['contrib', 'docs', 'tests']),
    #include_package_data=True,  
    
    package_data={
        '':["*.ui"], # include QT ui files 
        },
    
    )

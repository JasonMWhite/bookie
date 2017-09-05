import setuptools


setuptools.setup(
    name='bookie',
    version='0.0.1',
    description='Bookie',
    author='Jason White',
    author_email='actinolite.jw@gmail.com',
    url='https://github.com/JasonMWhite/bookie',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
)

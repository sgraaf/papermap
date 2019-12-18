import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    README = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='papermap',
    version='0.2',
    license='GNU General Public License (GNU GPL v3 or above)',
    author='Steven van de Graaf',
    author_email='steven@vandegraaf.xyz',
    description='A python package and CLI for creating paper maps',
    long_description=README,
    long_description_content_type='text/markdown',
    keywords='paper map image osm openstreetmap package cli',
    url='https://github.com/sgraaf/papermap',
    packages=['papermap'],
    install_requires=requirements,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['papermap = papermap.papermap:main']
    },
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    package_data = {
        'papermap': ['icons/map_marker.png']
    },
)
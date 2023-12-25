from setuptools import setup, find_packages


description_files = ['README.md', 'AUTHORS.md', 'CHANGELOG.md']

setup(
    name="arnold",
    description="RPi 4 Based Robotic Platform",
    long_description="".join([open(f, 'r').read() for f in description_files]),
    version="0.0.1",
    author='Hacklab',
    author_email="dev@hacklab.co.za",
    license="BSD",
    url="http://github.com/hacklabza/arnold",
    packages=find_packages(),
    dependency_links=[],
    install_requires=list(open('requirements.txt', 'r').read().splitlines()),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent"
    ],
    zip_safe=False,
    include_package_data=True,
    entry_points={'console_scripts': ['arnold = arnold.cli:cli']}
)

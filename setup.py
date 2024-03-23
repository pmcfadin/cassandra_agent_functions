from setuptools import setup, find_packages

setup(
    name='cassandra_agent_functions',
    version='0.1.0',
    author='Patrick McFadin',
    author_email='patrick@datastax.com',
    description='A library to facilitate AI agents interacting with Cassandra databases.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/cassandra_agent_functions',
    packages=find_packages(),
    install_requires=[
        'cassandra-driver>=3.25.0',
        # Other dependencies here
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

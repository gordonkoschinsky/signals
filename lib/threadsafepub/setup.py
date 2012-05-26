from distutils.core import setup

setup(
    name='ThreadSafePub',
    version='0.1.0',
    author='Frank Klein',
    author_email='nospam4gordon@gmail.com',
    packages=['threadsafepub'],
    scripts=[],
    url='http://pypi.python.org/pypi/threadsafepub/',
    license='LICENSE.txt',
    description='Simple wrapper to PyPubSub.pub threadsafe.',
    long_description=open('README.txt').read(),
    install_requires=[
        "PyPubSub"
    ],
)

from setuptools import setup

setup(name='remon',
      version='1.0',
      description='RemoteMonitor for remote nodes',
      url='https://github.com/sb00nk/ReMon',
      author='Andrea Uguzzoni',
      author_email='sb000nk@gmail.com',
      test_suite='test.TestSuite',
      packages=['src', 'test'],
      install_requires=['Pyro','fabric','pycrypto'],
      include_package_data=True)

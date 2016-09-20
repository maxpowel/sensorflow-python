from distutils.core import setup
setup(
    name='sensorflow',
    packages=['sensorflow'],
    version='1.1',
    description='Python driver for sensorflow devices',
    author='Alvaro Garcia Gomez',
    author_email='maxpowel@gmail.com',
    url='https://github.com/maxpowel/sensorflow-python',
    download_url='https://github.com/maxpowel/sensorflow-python/archive/master.zip',
    keywords=['sensor', 'arduino', 'data'],
    classifiers=['Topic :: Adaptive Technologies'],
    install_requires=['pyserial']
)
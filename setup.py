from setuptools import setup

setup(
    name='FlaskPlus',
    version='0.1',
    long_description=__doc__,
    packages=['flaskplus'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask']
)

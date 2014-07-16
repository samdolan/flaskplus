from setuptools import setup


def parse_requirements(requirements_path):
    """Parse a requirements.txt file as a list of requirements."""
    with open(requirements_path) as f:
        return [l.strip('\n') for l in f
                if l.strip('\n') and not l.startswith('#')]

requirements = parse_requirements('requirements.txt')

setup(
    name='FlaskPlus',
    version='0.1',
    long_description=__doc__,
    packages=['flaskplus'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
)

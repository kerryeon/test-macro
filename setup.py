from setuptools import find_packages, setup


author = {
    'name': 'Ho Kim',
    'email': 'ho.kim@gnu.ac.kr',
}


setup(
    name='test-macro',
    version='0.1',
    author=author['name'],
    author_email=author['email'],
    maintainer=author['name'],
    maintainer_email=author['email'],
    url=r'https://github.com/kerryeon/test-macro',
    license='MIT',
    description='a test automating library written in Python',
    platforms=[

    ],
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'macro=test_macro.macro:main',
        ],
    },
)

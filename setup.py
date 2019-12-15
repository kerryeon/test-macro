from setuptools import find_packages, setup

author = {
    'name': 'Ho Kim',
    'email': 'ho.kim@gnu.ac.kr',
}


setup(
    version='0.1',

    name='test-macro',
    description='a test automating library written in Python',
    url=r'https://github.com/kerryeon/test-macro',

    author=author['name'],
    author_email=author['email'],
    maintainer=author['name'],
    maintainer_email=author['email'],
    license='MIT',

    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'macro=test_macro.macro:main',
        ],
    },

    install_requires=[
        'ewmh',
        'lark-parser',
        'matplotlib',
        'mss',
        'opencv-python',
        'python-xlib',
        'PyYAML',
        'scipy',
        'tqdm',
    ],
    zip_safe=False,
)

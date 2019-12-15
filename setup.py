from setuptools import find_packages, setup

author = {
    'name': 'Ho Kim',
    'email': 'ho.kim@gnu.ac.kr',
}


def read(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


setup(
    version='0.1.1',

    name='test-macro',
    description='a test automating library written in Python',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
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

    include_package_data=True,
    zip_safe=False,
)

from setuptools import setup

setup(
    name='oauth4cli',
    version='0.1.0',
    description='Authorization code flow via Browser for the CLI',
    url='https://github.com/aruehl/oauth4cli',
    author='Andreas Rühl',
    author_email='andreas.ruehl@gmail.com',
    license='MIT',
    packages=[
        'oauth4cli'
    ],
    install_requires=[
        'flask',
        'requests',
        'requests-oauthlib',
        'werkzeug'
    ],
    zip_safe=False
)

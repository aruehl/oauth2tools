from setuptools import setup

setup(
    name='oauth4cli',
    version='0.2.0',
    description='The most straight forward way of using standard python libraries for a authorization code flow via Browser for the CLI.',
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

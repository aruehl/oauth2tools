from setuptools import setup

setup(
    name='oauth2tools',
    version='0.4.0',
    description='A toolset for the most requirements dealing with OAuth2',
    url='https://github.com/aruehl/oauth2tools',
    author='Andreas Rühl',
    author_email='andreas.ruehl@gmail.com',
    license='MIT',
    packages=[
        'oauth2tools'
    ],
    install_requires=[
        'flask',
        'requests',
        'requests-oauthlib',
        'werkzeug'
    ],
    zip_safe=False
)

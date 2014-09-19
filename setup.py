import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'waitress',
    'pyramid_fanstatic',
    'rebecca.fanstatic',
    'couchdbkit',
    'py-bcrypt',
    'js.bootstrap',
    'css.fontawesome',
    'pyramid_mailer',
    'js.jquery',
    'fanstatic',
#    'python-magic',
    'filemagic',
    'hachoir-metadata',
    'kombu',
    ]

setup(name='chaton',
      version='0.0',
      description='chaton',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="chaton",
      entry_points="""\
      [paste.app_factory]
      main = chaton:main
      [console_scripts]
      adduser = chaton.utils:addUser
      metadata = chaton.metadatadaemon:main
      encode = chaton.reencode:main
      [fanstatic.libraries]
      chaton = chaton.resources:library
      """,
      )

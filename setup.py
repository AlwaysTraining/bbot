from distutils.core import setup 

setup(name="bbot",
      version="0.1",
      packages = ['bbot'],
      py_modules = [
          'bbot.App',
          'bbot.Constants',
          ],
      scripts = ['bin/bbot.py',
                ],
      author = ['Derrick Karimi'],
      author_email = [ 'derrick.karimi@gmail.com' ],
      maintainer = ['Derrick Karimi'],
      maintainer_email = ['derrick.karimi@gmail.com'],
      description = ['bbot'],
      url = ['https://github.com/AlwaysTraining/bbot'],
      download_url = ['https://github.com/AlwaysTraining/bbot'])

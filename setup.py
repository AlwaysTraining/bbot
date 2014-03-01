from distutils.core import setup
from os import  path
from glob import glob

def get_modules():
    objdir = path.join(path.dirname(__file__),'bbot/*.py')
    mods=[]
    for file in glob(objdir):
        name = path.splitext(path.basename(file))[0]
        if name == '__init__':
            continue
        mods.append("bbot." + name)
    return mods

setup(name="bbot",
      version="0.1",
      packages = ['bbot'],
      py_modules = get_modules(),
      scripts = ['bin/bbot-cli.py'],
      author = ['Derrick Karimi'],
      author_email = [ 'derrick.karimi@gmail.com' ],
      maintainer = ['Derrick Karimi'],
      maintainer_email = ['derrick.karimi@gmail.com'],
      description = ['bbot'],
      url = ['https://github.com/AlwaysTraining/bbot'],
      download_url = ['https://github.com/AlwaysTraining/bbot'],
      install_requires=['pexpect<=2.3'])

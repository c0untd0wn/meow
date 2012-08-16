import sys
import os

current_platform = sys.platform

# Mac OS X
if current_platform == 'darwin':
  os.system("python setup.py bdist_dmg")
elif current_platform == 'win32':
  os.system("python setup.py bdist_msi")
elif current_platform == 'linux2':
  os.system("python setup.py bdist_rpm")
else:
  os.system("python setup.py install_exe")

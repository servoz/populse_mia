"""Idea: Create a zip containing MIA_Processes folder, protected by a password
It is easy to zip/unzip with a password using zipfile
But the password has to be strong (use md5 ?) and totally hidden for the user

from zipfile import ZipFile
import os
import zipfile

# Taken from stackoverflow
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

if __name__ == '__main__':
    zipf = zipfile.ZipFile('Python.zip', 'w', zipfile.ZIP_DEFLATED)
    pswd = b"ANYPASSWORD"
    zipf.setpassword(pswd)
    zipdir('tmp/', zipf)
    zipf.close()

    # To unzip
    with zipfile.ZipFile('Python.zip') as zf:
        zf.extractall(pwd=pswd)
"""

import lib
import os
import sys

if __name__ == '__main__':
    np = lib.NeoPage('/')
    user = os.environ['NP_USER']
    pswd = os.environ['NP_PASS']
    np.login(user, pswd)

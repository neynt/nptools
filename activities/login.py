import sys
import lib

if __name__ == '__main__':
    np = lib.NeoPage('/')
    np.login(sys.argv[1], sys.argv[2])

import os
import sys

from .cli import main

if __name__ == '__main__':
    try:
        sys.exit(main() or 0)
    except Exception:
        if os.getenv('APATITE_DEBUG'):
            import pdb;pdb.post_mortem()
        raise

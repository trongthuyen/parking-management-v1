print('\033[92m')
import os
import sys

splited_absolute_path = __file__.replace('\\', '/').split('/')
splited_absolute_path.pop()
absolute_path = os.path.dirname('/'.join(splited_absolute_path))
sys.path.append(absolute_path)
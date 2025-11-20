'''
A script designed to run Django in a third-party folder
'''

import os
import sys
import django


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brainua_project.settings')

django.setup()

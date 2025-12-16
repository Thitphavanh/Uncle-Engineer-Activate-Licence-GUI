"""
Settings package for core project.
Import appropriate settings based on DJANGO_ENV environment variable.
"""

import os

env = os.getenv('DJANGO_ENV', 'development')

if env == 'production':
    from .prod import *
elif env == 'development':
    from .dev import *
else:
    from .base import *

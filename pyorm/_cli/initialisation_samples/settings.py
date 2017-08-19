""" Settings for the pyorm framework
    
    Check individual comments for details of each section
"""

#
#  By default the pyorm framework uses pathlib
#
from pathlib import Path

#
# Import the intended database engine
#
import pyorm.db.engine.sqlite

#
# Shortcut to the project file
#
PROJ = Path(__file__).parent()

# dataabase details - this dictionary MUST always exist
#
# Keys:
#   'database': The path to the application database
#   'engine' : The Engine class of the appropruate db engine module
#
db = { 'database': PROJ / 'database.db',
       'engine': db.engine.sqlite.Engine}


#
# Setting for the models directory - change with care
#
models = PROJ / 'models'


#
# Setting for the models directory - change with care
#
migration = PROJ / 'migrations'
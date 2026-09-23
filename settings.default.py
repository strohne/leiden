#
# This is a blueprint: Copy the file to settings.py and add your credentials
# Git will ignore the settings.py
#
# Import it into your scripts:
# ```
# import settings
# ```
#


# Epigraf settings
import epygraf as epi

# epi.api.setup(
#     "https://epigraf-dev.uni-muenster.de",
#     "YOURTOKEN"
# )

epi.api.setup(
    "http://127.0.0.1",
    "devel"
)

epi.db.setup(
    host="127.0.0.3",
    port=3306,
    username="root",
    password="root"
)


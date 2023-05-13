import os
from app import celery, create_app
from decouple import config

from config import config_dict


# WARNING: Don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True)

get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    
    # Load the configuration using the default values 
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app( app_config )


app.app_context().push()
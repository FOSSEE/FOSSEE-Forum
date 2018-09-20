#!/bin/bash

chmod -R 777 /Sites/newforums_fossee_in/django

source /Sites/newforums_fossee_in/django/bin/activate

python /Sites/newforums_fossee_in/FOSSEE-Forum/website/cron.py

deactivate
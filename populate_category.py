from builtins import str
import os
import datetime
import django
from datetime import timedelta

Date = datetime.datetime.now()
def populate():
    #file_obj = open("data_of_rc.csv")
    #print file_obj
    #file_obj.close()
    f = open("category_names.txt")
    for line in f:
        cname = line.replace("\n", "")
        cat_added = add_category(cname)
    f.close()

def add_category(cname):
    cat = FossCategory.objects.get_or_create(name = cname, description = cname, date_created = Date, date_modified = Date)[0]#for now description is same as category_names
    print("category " +str(cname)+" added at "+str(Date))
    return cat

# Start execution here!
if __name__ == '__main__':
    print("Starting population script for adding category...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forums.settings')
    django.setup()
    from website.models import *
    populate()

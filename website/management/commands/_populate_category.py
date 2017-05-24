import os
import datetime
from datetime import timedelta
from website.models import *

Date = datetime.datetime.now()
def populate():
	f=open("category_names.txt")
	for line in f:
		cname=line.replace("\n","")
		cat_added=add_category(cname)
	f.close()

def add_category(cname):
	# this function will add all the elements to the FossCatagory table in database
    cat = FossCategory.objects.get_or_create(name=cname,
    										 description=cname,
    										 date_created=Date,
    										 date_modified=Date)[0]
    #for now description is same as category_names
    print "category " +str(cname)+" added at "+str(Date)
    return cat



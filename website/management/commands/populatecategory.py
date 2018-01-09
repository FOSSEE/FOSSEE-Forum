from django.core.management.base import BaseCommand, CommandError
import os
import datetime
from datetime import timedelta
from website.models import *

Date = datetime.datetime.now()


class Command(BaseCommand):

    def populate(self):
        f = open("category_names.txt")
        for line in f:
            line = line.replace("\n", "")
            details = line.split(',')
            cname = details[0]
            cemail = details[1]
            self.add_category(cname, cemail)
        f.close()

    def add_category(self, cname, cemail):
        cat = FossCategory.objects.get_or_create(name=cname, description=cname,
                                                 date_created=Date,
                                                 date_modified=Date,
                                                 email=cemail)[0]
        print "category " + str(cname) + " added at " + str(Date)
        return cat

    def handle(self, *args, **options):
        print "Starting population script for adding category..."
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forums.settings')
        from website.models import *
        self.populate()

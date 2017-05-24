from django.core.management.base import BaseCommand, CommandError
from _populate_category import *

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        print "Starting population script for adding category..."
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forums.settings')
        from website.models import *
 		# populate function present in _populate_category.py
        populate()

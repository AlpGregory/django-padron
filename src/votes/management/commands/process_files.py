import time
import os

from django.core.management.base import BaseCommand
from votes.utils import FileDecoder
from padron_web.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Processes two txt files and upload them to a database'

    def add_arguments(self, parser):
        parser.add_argument('register_files', nargs=2, type=str)

    def handle(self, *args, **options):
        start = time.perf_counter()
        folder_path = os.path.join(BASE_DIR, '../fixtures/')
        people_path = folder_path + options['register_files'][0]
        locations_path = folder_path + options['register_files'][1]

        decoder = FileDecoder()
        decoder.process_files(locations_path=locations_path, people_path=people_path)

        execution_time = time.perf_counter() - start
        print(f"Execution time in seconds: {execution_time}")

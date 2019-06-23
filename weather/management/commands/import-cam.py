import datetime
import glob
import os
import re
from shutil import copyfile

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.timezone import make_aware

from weather.models import WeatherImages
from weather.utilities import translate_date


class Command(BaseCommand):
    help = "Update weather station data from the Ambient Weather API."
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    def handle(self, *args, **options):
        self.verbosity = int(options["verbosity"])

        file_date_pattern = '\D(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})'
        file_time_pattern = '(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})'

        source_folder = os.path.join('/', 'home', 'avryhof', 'weather')

        target_folder = os.path.join(settings.MEDIA_ROOT, 'weather')
        if not os.path.exists(target_folder):
            try:
                os.mkdir(target_folder)
            except:
                print('Failed to create weather folder.')
            else:
                print('weather folder created.')

        for date_folder in glob.glob(os.path.join(source_folder, '*')):
            if os.path.isdir(date_folder):
                folder_name = os.path.split(date_folder)[-1]
                target_date_folder = os.path.join(target_folder, folder_name)
                if not os.path.exists(target_date_folder):
                    try:
                        os.mkdir(target_date_folder)
                    except:
                        print('Failed to create %s' % target_date_folder)
                    else:
                        print('Folder created: %s' % target_date_folder)

                folder_date = translate_date(folder_name)

                image_folder = (os.path.join(date_folder, 'images'))
                target_image_folder = os.path.join(target_date_folder, 'images')
                if not os.path.exists(target_image_folder):
                    try:
                        os.mkdir(target_image_folder)
                    except:
                        print('Failed to create %s' % target_image_folder)
                    else:
                        print('Image folder created.')

                for image in glob.glob(os.path.join(image_folder, '*.jpg')):
                    image_name = os.path.split(image)[-1]
                    target_image = os.path.join(target_image_folder, image_name)

                    if not os.path.exists(target_image):
                        try:
                            copyfile(image, target_image)
                        except:
                            print('Failed to copy file.')

                        else:
                            image_time_pattern = '%s%s' % (file_date_pattern, file_time_pattern)
                            try:
                                image_date_parts = re.search(image_time_pattern, image_name).groups()

                            except AttributeError:
                                print(image_name)

                            else:
                                file_time = make_aware(datetime.datetime(
                                    year=2000 + int(image_date_parts[0]),
                                    month=int(image_date_parts[1]),
                                    day=int(image_date_parts[2]),
                                    hour=int(image_date_parts[3]),
                                    minute=int(image_date_parts[4]),
                                    second=int(image_date_parts[5]),
                                ))

                                try:
                                    WeatherImages.objects.create(
                                        date=folder_date,
                                        time=file_time,
                                        filename=image_name,
                                        path=target_image,
                                        url=target_image.replace(settings.MEDIA_ROOT, settings.MEDIA_URL).replace('//', '/')
                                    )

                                except:
                                    print('Failed to create database entry.')

                                else:
                                    os.remove(image)

from hiking.models import HikeSource
from utilities.command_baseclass import ManagementCommand
from utilities.debugging import log_message
from web_discover.models import WebPath


class Command(ManagementCommand):
    def handle(self, *args, **options):
        target_url = "https://www.cnyhiking.com/index.html"

        try:
            hike_src = HikeSource.objects.get(url=target_url)
        except HikeSource.DoesNotExist:
            try:
                site = WebPath.objects.get(url=target_url)
            except WebPath.DoesNotExist:
                site = WebPath.objects.create(url=target_url)

            hike_src = HikeSource.objects.create(url=target_url)

        links = hike_src.webpath.links

        region_qualifiers = ['Adirondack', 'Onondaga', 'Catskill', 'NorthCountry', 'Waterfalls', 'FireTower',
                             'GreatEastern', 'NewYorkStateParks', 'HikingInCentralNewYork', 'MorganHillStateForest',
                             'FingerLakesNationalForest', "AppalachianTrail", "LinkTrail", "FingerLakesTrail",
                             "LongPath", "Northville-PlacidTrail", "NationalScenicTrails"]

        regions = []
        for link in links:
            for region_qualifier in region_qualifiers:
                if region_qualifier in link:
                    regions.append(link)

        regions = sorted(regions)

        for region in regions:
            try:
                HikeSource.objects.get(url=region)
            except HikeSource.DoesNotExist:
                HikeSource.objects.create(url=region)

        for hike_source in HikeSource.objects.all():
            

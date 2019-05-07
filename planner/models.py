from django.db import models
from django.db.models import DO_NOTHING
from django.urls import reverse


class CalendarItemType(models.Model):
    """
    An abstract base type for Types of Calendar Items
    """
    name = models.CharField(max_length=200, null=True)
    description = models.TextField(blank=True, null=True)
    default_start_time = models.TimeField(blank=True, null=True)
    default_end_time = models.TimeField(blank=True, null=True)

    class Meta:
        abstract = True


class CalendarItem(models.Model):
    """
    An Abstract base class for calendar items, such as meals or Events.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    @property
    def get_url(self):
        url = None

        try:
            url = reverse('planner:event_edit', args=(self.pk,))
        except:
            pass

        return url


class EventType(CalendarItemType):

    def __str__(self):
        return self.name


class Event(CalendarItem):
    event_type = models.ForeignKey(EventType, null=True, on_delete=DO_NOTHING)

    def __str__(self):
        retn = self.event_type.name

        if self.title:
            retn = '%s: %s' % (self.event_type.name, self.title)

        return retn


class MealType(CalendarItemType):

    def __str__(self):
        return self.name


class Meal(CalendarItem):
    meal = models.ForeignKey(MealType, null=True, on_delete=DO_NOTHING)
    recipe = models.TextField(blank=True, null=True)
    recipe_url = models.URLField(blank=True, null=True)

    def __str__(self):
        retn = self.meal.name

        if self.title:
            retn = '%s: %s' % (self.meal.name, self.title)

        return retn

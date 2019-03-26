from django.db import models

from planner.constants import BUDGET_CHOICES, BUDGET_EXPENSE


class BudgetItem(models.Model):
    item_type = models.CharField(max_length=32, choices=BUDGET_CHOICES, default=BUDGET_EXPENSE)
    description

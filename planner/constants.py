BUDGET_DEBT = "debt"
BUDGET_EXPENSE = "expense"
BUDGET_INCOME = "income"
BUDGET_SAVINGS = "savings"
BUDGET_CHOICES = (
    (BUDGET_DEBT, "Debt"),
    (BUDGET_EXPENSE, "Expense"),
    (BUDGET_INCOME, "Income"),
    (BUDGET_SAVINGS, "Savings"),
)

MEAL_BREAKFAST = "breakfast"
MEAL_BRUNCH = "breakfast"
MEAL_LUNCH = "lunch"
MEAL_DINNER = "dinner"
MEAL_SUPPER = "supper"

MEALS = {
    MEAL_BREAKFAST: "Breakfast",
    MEAL_BRUNCH: "Brunch",
    MEAL_LUNCH: "Lunch",
    MEAL_DINNER: "Dinner",
}

MEAL_CHOICES = (
    (MEAL_BREAKFAST, "Breakfast"),
    (MEAL_BRUNCH, "Brunch (a meal that replaces Breakfast and Lunch)"),
    (MEAL_LUNCH, "Lunch"),
    (MEAL_DINNER, "Dinner (a meal that replaces Lunch and Supper)"),
    (MEAL_SUPPER, "Supper"),
)

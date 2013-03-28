import db

class Recipe:
    def __init__(self, name, ingredientList):
        self.name = name
        self.ingredients = []
        for item in ingredientList:
            self.ingredients.append(item)
    
    def need_ingredients(self):
        # Start by creating a temp dict of remaining liquor needed in ml
        ingredientsRemaining = {}
        for (n, a) in self.ingredients:
            ingredientsRemaining[n] = db.convertToMl(a)
        
        # Then gets total liquor of each type from db, subtracts, and returns final list
        filledIngredients = []
        for n in ingredientsRemaining:
            ingredientsRemaining[n] -= db.check_inventory_for_type(n)
            if ingredientsRemaining[n] <= 0:
                filledIngredients.append(n)

        for n in filledIngredients:
            del ingredientsRemaining[n]

        returnedList = []
        for n in ingredientsRemaining:
            returnedList.append((n, ingredientsRemaining[n]))

        return returnedList

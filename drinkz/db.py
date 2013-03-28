"""
Database functionality for drinkz information.
"""

from sets import Set
from cPickle import dump, load

# private singleton variables at module level
_bottle_types_db = set()
_inventory_db = dict()
_recipe_db = dict()

def _reset_db():
    "A method only to be used during testing -- toss the existing db info."
    global _bottle_types_db, _inventory_db, _recipe_db
    _bottle_types_db = set()
    _inventory_db = dict()
    _recipe_db = dict()

def save_db(filename):
    fp = open(filename, 'wb')

    tosave = (_bottle_types_db, _inventory_db, _recipe_db)
    dump(tosave, fp)

    fp.close()

def load_db(filename):
    global _bottle_types_db, _inventory_db, _recipe_db
    fp = open(filename, 'rb')

    loaded = load(fp)
    (_bottle_types_db, _inventory_db, _recipe_db) = loaded

    fp.close()

# exceptions in Python inherit from Exception and generally don't need to
# override any methods.
class LiquorMissing(Exception):
    pass
class DuplicateRecipeName(Exception):
    pass

def add_bottle_type(mfg, liquor, typ):
    "Add the given bottle type into the drinkz database."
    _bottle_types_db.add((mfg, liquor, typ))

def _check_bottle_type_exists(mfg, liquor):
    for (m, l, _) in _bottle_types_db:
        if mfg == m and liquor == l:
            return True

    return False

def add_to_inventory(mfg, liquor, amount):
    "Add the given liquor/amount to inventory."
    if not _check_bottle_type_exists(mfg, liquor):
        err = "Missing liquor: manufacturer '%s', name '%s'" % (mfg, liquor)
        raise LiquorMissing(err)

    if (mfg, liquor) not in _inventory_db:
        _inventory_db[(mfg, liquor)] = amount
    else:
        _inventory_db[(mfg, liquor)] = str(float(_inventory_db[(mfg, liquor)].split()[0]) + convertToMl(amount)) + " ml"

def convertToMl(inputAmount):
    amount = float(inputAmount.split()[0])
    unit = inputAmount.split()[1]

    if unit == "ml":
        return amount
    elif unit == "oz":
        return amount * 29.5735
    elif unit == "gallon" or unit == "gallons":
        return amount * 3785.41
    elif unit == "liter":
        return amount * 1000.0
    else:
        raise Exception("Unknown unit: ", unit)
    return 0

def check_inventory(mfg, liquor):
    for (m, l) in _inventory_db:
        if mfg == m and liquor == l:
            return True
        
    return False

def get_liquor_amount(mfg, liquor):
    "Retrieve the total amount of any given liquor currently in inventory."
    total = float(0);
    for (m, l) in _inventory_db:
        if mfg == m and liquor == l:
            amountText = _inventory_db[(m,l)]
            total += convertToMl(amountText)
    return total

def get_liquor_inventory():
    "Retrieve all liquor types in inventory, in tuple form: (mfg, liquor)."
    for (m, l) in _inventory_db:
        yield m, l

def add_recipe(recipe):
    if _recipe_db.has_key(recipe.name) == False:
        _recipe_db[recipe.name] = recipe
    else:
        raise DuplicateRecipeName

def get_recipe(name):
    return _recipe_db.get(name)

def get_all_recipes():
    for recipe in _recipe_db:
        yield _recipe_db[recipe]

def check_inventory_for_type(type):
    total = 0.0
    liquorsGrabbed = Set([])
    for (m, l, t) in _bottle_types_db:
        if t == type and (l not in liquorsGrabbed or t > total):
            total = convertToMl(_inventory_db[(m,l)])
            liquorsGrabbed.add(l)
    return total

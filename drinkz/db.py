"""
Database functionality for drinkz information.
"""

from sets import Set
from cPickle import dump, load
import sys
import sqlite3 as lite

class Party:
    def __init__(self, user, title, date, time, address, recipes, liquors):
        self.user = user
        self.title = title
        self.date = date
        self.time = time
        self.address = address
        self.recipes = recipes #dict
        self.liquors = liquors #dict
        self.attending = [user] #list

    def add_attending(self, name):
        self.attending.append(name)

    def add_liquor(self, liquors):
        for (m, l) in liquors:
            if not self.liquors.has_key((m,l)):
                self.liquors[(m, l)] = liquors[(m, l)]
            else:
                self.liquors[(m, l)] += liquors[(m, l)]

# private singleton variables at module level
_bottle_types_db = set()
_inventory_db = dict()
_recipe_db = dict()
_parties = []

def _reset_db():
    "A method only to be used during testing -- toss the existing db info."
    global _bottle_types_db, _inventory_db, _recipe_db
    _bottle_types_db = set()
    _inventory_db = dict()
    _recipe_db = dict()
    _parties = []

def save_db(filename):
    fp = open(filename, 'wb')

    tosave = (_bottle_types_db, _inventory_db, _recipe_db, _parties)
    dump(tosave, fp)

    fp.close()

def load_db(filename):
    global _bottle_types_db, _inventory_db, _recipe_db, _parties
    fp = open(filename, 'rb')

    loaded = load(fp)
    (_bottle_types_db, _inventory_db, _recipe_db, _parties) = loaded

    fp.close()

def save_db_sqlite(filename):
    con = lite.connect(filename + '.db')
    with con:
        cur = con.cursor()

        # Save bottle types
        cur.execute("DROP TABLE IF EXISTS bottle_types")
        cur.execute("CREATE TABLE bottle_types (m TEXT, l TEXT, t TEXT)")
        for (m, l, t) in _bottle_types_db:
            cur.execute("INSERT INTO bottle_types VALUES ('" + m + "', '" + l + "', '" + t + "')")

        # Save inventory
        cur.execute("DROP TABLE IF EXISTS inventory")
        cur.execute("CREATE TABLE inventory (m TEXT, l TEXT, a TEXT)")
        for (m, l) in _inventory_db:
            cur.execute("INSERT INTO inventory VALUES ('" + m + "', '" + l + "', '" + _inventory_db[(m, l)] + "')")

        # Save recipes
        cur.execute("DROP TABLE IF EXISTS recipes")
        cur.execute("CREATE TABLE recipes (n TEXT, i TEXT)")
        for n in _recipe_db:
            ingredients = ""
            for i in _recipe_db[n]:
                ingredients += i[0] + "|" + i[1] + ","
            cur.execute("INSERT INTO recipes VALUES ('" + n + "', '" + ingredients + "')")

        # Save parties
        cur.execute("DROP TABLE IF EXISTS parties")
        cur.execute("CREATE TABLE parties (user TEXT, title TEXT, date TEXT, time TEXT, address TEXT, recipes TEXT, liquors TEXT, attending TEXT)")
        for p in _parties:
            recipes = ""
            for r in p.recipes:
                recipes += r + ","
                for i in p.recipes[r]:
                    recipes += i[0] + "|" + i[1] + ","
                recipes += "$"
            liquors = ""
            for (m, l) in p.liquors:
                liquors += m + "," + l + "," + str(p.liquors[(m, l)]) + "$"
            attending = ""
            for a in p.attending:
                attending += a + ","
            cur.execute("INSERT INTO parties VALUES ('" + p.user + "', '" + p.title + "', '" + p.date + "', '" + p.time + "', '" + p.address + "', '" + recipes + "', '" + liquors + "', '" + attending + "')")

def load_db_sqlite(filename):
    con = lite.connect(filename + '.db')
    global _bottle_types_db, _inventory_db, _recipe_db, _parties
    with con:
        # Load bottle types
        cur = con.cursor()
        cur.execute("SELECT * FROM bottle_types")
        rows = cur.fetchall()
        for row in rows:
            _bottle_types_db.add((str(row[0]), str(row[1]), str(row[2])))

        # Load inventory
        cur.execute("SELECT * FROM inventory")
        rows = cur.fetchall()
        for row in rows:
            _inventory_db[(str(row[0]), str(row[1]))] = str(row[2])

        # Load recipes
        cur.execute("SELECT * FROM recipes")
        rows = cur.fetchall()
        for row in rows:
            name = str(row[0])
            ingredients = ()
            for i in row[1].split(","):
                if i == '':
                    continue
                sep = i.split("|")
                ingredients += (str(sep[0]), str(sep[1])),
            _recipe_db[name] = ingredients

        # Load parties
        cur.execute("SELECT * FROM parties")
        rows = cur.fetchall()
        for row in rows:
            user = str(row[0])
            title = str(row[1])
            date = str(row[2])
            time = str(row[3])
            address = str(row[4])
            
            recipes = dict()
            raw_recipes = row[5].split("$")
            for r in raw_recipes:
                if r == '':
                    continue
                split_recipes = r.split(",")
                name = str(split_recipes[0])
                ingredients = ()
                for i in range(1, len(split_recipes)-1):
                    if split_recipes[i] == '':
                        continue
                    sep = split_recipes[i].split("|")
                    ingredients += (str(sep[0]), str(sep[1])),
                recipes[name] = ingredients
            
            liquors = dict()
            raw_liquors = row[6].split("$")
            for l in raw_liquors:
                if l == '':
                    continue
                split_liquors = l.split(",")
                m = str(split_liquors[0])
                l = str(split_liquors[1])
                a = str(split_liquors[2])
                liquors[(m,l)] = a
            
            attending = []
            for u in row[7].split(","):
                if u == '':
                    continue
                attending.append(str(u))

            addedParty = Party(user, title, date, time, address, recipes, liquors)
            addedParty.attending = attending
            _parties.append(addedParty)

# exceptions in Python inherit from Exception and generally don't need to
# override any methods.
class LiquorMissing(Exception):
    pass
class DuplicateRecipeName(Exception):
    pass

def add_party(party):
    for p in _parties:
        if p.user == party.user:
            return False
    _parties.append(party)
    return True

def get_party(user):
    for p in _parties:
        if p.user == user:
            return p
    return None

def get_all_parties():
    for p in _parties:
        yield p

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

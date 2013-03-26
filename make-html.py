import os, sys
from drinkz import db, recipes

try:
    os.mkdir('html')
except OSError:
    pass

db.add_bottle_type('Johnnie Walker', 'black label', 'blended scotch')
db.add_to_inventory('Johnnie Walker', 'black label', '500 ml')

db.add_bottle_type('Uncle Herman\'s', 'moonshine', 'blended scotch')
db.add_to_inventory('Uncle Herman\'s', 'moonshine', '5 liter')
        
db.add_bottle_type('Gray Goose', 'vodka', 'unflavored vodka')
db.add_to_inventory('Gray Goose', 'vodka', '1 liter')

db.add_bottle_type('Rossi', 'extra dry vermouth', 'vermouth')
db.add_to_inventory('Rossi', 'extra dry vermouth', '24 oz')

r = recipes.Recipe('vodka martini', [('unflavored vodka', '6 oz'), ('vermouth', '1.5 oz')])
db.add_recipe(r)
r = recipes.Recipe('Gin and Tonic', [('gin', '2 oz'), ('tonic water', '5 oz')])
db.add_recipe(r)

###

fp = open('html/index.html', 'w')

print >>fp, """CSE 491 - Homework #3 - Alex Lockwood - v1.1
<p>
<a href='recipes.html'>Recipe List</a>
<p>
<a href='inventory.html'>Inventory</a>
<p>
<a href='liquor_types.html'>Liquor Types</a>
"""

fp.close()

###

fp = open('html/recipes.html', 'w')

print >>fp, "<a href='/'>Back to Index</a><p><ul>"

for recipe in db.get_all_recipes():
    print >>fp, "<li> ", recipe.name, ": "
    if not recipe.need_ingredients():
        print >>fp, "AVAILABLE"
    else:
        print >>fp, "NEED "
        for (l, a) in recipe.need_ingredients():
            print >>fp, l, " - ", a, "ml, "
fp.close()

###

fp = open('html/inventory.html', 'w')

print >>fp, "<a href='/'>Back to Index</a><p><ul>"

for (m, f) in db._inventory_db:
    print >>fp, "<li> ", m, " - ", f, " - ", db._inventory_db[(m, f)]

fp.close()

###

fp = open('html/liquor_types.html', 'w')

print >>fp, "<a href='/'>Back to Index</a><p><ul>"

for (m, f, g) in db._bottle_types_db:
    print >>fp, "<li> ", m, " - ", f, " - ", g

print >>fp, "</ul>"


fp.close()

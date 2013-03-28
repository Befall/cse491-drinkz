# Init clean database w/ data, create new SimpleApp object,
# call __call__ func w/ 'environ' dic and 'start_response' of my own,
# run code to generate recipe page, checks that data is correct
# god damnit

from wsgiref.simple_server import make_server
import urlparse
import simplejson
import drinkz.recipes
from drinkz import db
from app import SimpleApp

def populate_database():
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

if __name__ == '__main__':
    import random, socket
    port = random.randint(8000, 9999)
    
    #create environ/start_response
    environ = {}
    environ['PATH_INFO'] = '/'
    
    d = {}
    def my_start_response(s, h, return_in=d):
        d['status'] = s
        d['headers'] = h

#    populate_database()
#    assert db._recipe_db.has_key('vodka martini')
#    assert db._recipe_db.has_key('whiskey sour') == False
    db.load_db('../bin/drinkz.txt')

    app = SimpleApp()
    results = app(environ, my_start_response)
    
    text = "".join(results)
    status, headers = d['status'], d['headers']
    
    assert text.find('Table of Contents') != -1, text
    assert ('Content-Type', 'text/html') in headers
    assert status == '200 OK'

    httpd = make_server('', port, app)
    print "Serving on port %d..." % port
    print "Try using a Web browser to go to http://%s:%d/" % \
          (socket.getfqdn(), port)
    httpd.serve_forever()

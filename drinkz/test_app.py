# Init clean database w/ data, create new SimpleApp object,
# call __call__ func w/ 'environ' dic and 'start_response' of my own,
# run code to generate recipe page, checks that data is correct
# god damnit

import os, sys

# get the current working directory
thisdir = os.path.dirname(__file__)

# build path to directory containing drinkz/ lib directory for imports
libdir = os.path.join(thisdir, '../')
libdir = os.path.abspath(libdir)

# add it into sys.path first, so that 'import' will find it first.
sys.path.insert(0, libdir)

from wsgiref.simple_server import make_server
import urlparse
import simplejson
from drinkz import db, recipes, app
from drinkz.app import SimpleApp
from drinkz.db import Party

def populate_database():
    db.add_bottle_type('Johnnie Walker', 'black label', 'blended scotch')
    db.add_to_inventory('Johnnie Walker', 'black label', '500 ml')

    db.add_bottle_type('Uncle Hermans', 'moonshine', 'blended scotch')
    db.add_to_inventory('Uncle Hermans', 'moonshine', '5 liter')
        
    db.add_bottle_type('Gray Goose', 'vodka', 'unflavored vodka')
    db.add_to_inventory('Gray Goose', 'vodka', '1 liter')

    db.add_bottle_type('Rossi', 'extra dry vermouth', 'vermouth')
    db.add_to_inventory('Rossi', 'extra dry vermouth', '24 oz')

    derp = dict()
    r = recipes.Recipe('vodka martini', [('unflavored vodka', '6 oz'), ('vermouth', '1.5 oz')])
    db.add_recipe(r)
    derp[r.name] = r    
    r = recipes.Recipe('Gin and Tonic', [('gin', '2 oz'), ('tonic water', '5 oz')])
    db.add_recipe(r)
    derp[r.name] = r    
    herp = dict()
    herp[('Johnnie Walker', 'black label')] = 1000
    herp[('Gray Goose', 'vodka')] = 500    

    party1 = Party("Befall", "Get Drunk Party", "05-03-13", "11:00pm", "123 Balls St.", derp, herp)
    db.add_party(party1)
    db.save_db('bin\drinkz.txt')

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

    populate_database()
    db.load_db('bin\drinkz.txt')

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

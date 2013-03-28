#! /usr/bin/env python
import sys
import simplejson
import urllib2
import StringIO
from app import SimpleApp
import db, recipes

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

def call_remote(base, method, params, id):
    info = dict(base=base, method=method, params=params, id=id)
    jsonInfo = simplejson.dumps(info)
    output = StringIO.StringIO()
    output.write(jsonInfo)
    output.seek(0)

    environ = {}
    environ['PATH_INFO'] = '/rpc'
    environ['REQUEST_METHOD'] = 'POST'
    environ['wsgi.input'] = output
    environ['CONTENT_LENGTH'] = len(jsonInfo)

    d = {}
    def my_start_response(s, h, return_in=d):
        d['status'] = s
        d['headers'] = h

    app = SimpleApp()
    results = app(environ, my_start_response)

    result = StringIO.StringIO()
    result.write(results[0])
    result.seek(0)

    newResults = simplejson.loads(result.read(len(results[0])))

    return newResults['result']

if __name__ == '__main__':
    populate_database()
    print call_remote(base='1.0', method='convert_units_to_ml', params=['25 oz'], id=1)
    print call_remote(base='1.0', method='get_recipe_names', params=[], id=1)
    print call_remote(base='1.0', method='get_liquor_inventory', params=[], id=1)

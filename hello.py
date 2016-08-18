#!/usr/bin/env python
# stdlib

# other 3rd-party libs
import liblo

import flask
from flask import Flask


# local libs
import map_to_lighthouse_pan_angle
from map_to_lighthouse_pan_angle import (
    camp_to_man_xy,
    art_to_man_xy,
    lighthouse_camp_to_theta_degrees,
    )

app = Flask(__name__)
app.config['DEBUG'] = True

camps = [
    (3,'e'),
    (6,'e'),
    (8,'l'),
    (9,'a'),
    (9,'c'),
    (10,'b'),
    ]

osc_server = liblo.Address('127.0.0.1', 8000)

@app.route("/")
def foo():
    return flask.render_template('index.html', body='food', foo=[1,2,3])

@app.route("/goto201")
def goto201():
    things = []
    for camp in camps:
        thing = map_to_lighthouse_pan_angle.lighthouse_camp_to_theta_degrees(map_to_lighthouse_pan_angle.camp_to_man_xy(*camp))
        things.append(thing)
        
    #return "Hello World! %s" % (str('<br>'.join(int(things))),)
    rotate_to = lighthouse_camp_to_theta_degrees(camp_to_man_xy(3, 'e'))

    liblo.send(osc_server, '/staticLight/pan', float(rotate_to))

    return flask.Response(status=200)

    return str(foo)

#@app.errorhandler(werkzeug.exceptions.BadRequest)
#def handle_bad_request(e):
#    return 'bad request!'

if __name__ == "__main__":
    app.run()

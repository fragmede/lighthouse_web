#!/usr/bin/env python
# stdlib

# other 3rd-party libs
import flask
import liblo
import numpy as np

from flask import Flask, request

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
def root():
    return flask.render_template('index.html')

@app.route("/pan_to_coord/map_<int:map_width>x<int:map_height>/lh_<int:lh_left>x<int:lh_top>")
def pan_to_coord(map_width, map_height, lh_left, lh_top):
    args = request.args.keys()[0]
    image_x, image_y = [int(q) for q in args.split(',')]

    x, y = (image_x - lh_left), (image_y - lh_top)
    raw_theta = np.degrees(np.arctan2(y, x))
    lighthouse_theta = 180 + raw_theta
    print y, x, lighthouse_theta
    liblo.send(osc_server, '/staticLight/pan', lighthouse_theta)

    return flask.Response(status=204)

if __name__ == "__main__":
    app.run()

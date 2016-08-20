#!/usr/bin/env python
# stdlib

# other 3rd-party libs
import flask
import liblo
import numpy as np
import ujson as json
#import rapidjson as json

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

camp_list = json.load(open('data/camps.2015.json'))

@app.route("/camp_search/")
def camp_search():
    args = request.args.get('term')
    if not args:
        return json.dumps([])

    filtered_list_of_camps = []
    l_args = args.lower()
    for camp in camp_list:
        if l_args in camp['name'].lower():
            obj_loc = camp['location']
            if not obj_loc['string']:
                # Mobile and test data don't have locations
                continue
            frontage = obj_loc['frontage']
            intersection = obj_loc['intersection']
            if frontage == 'Esplanade':
                frontage = 'z' # magic value defined in map_to_l...py
            if len(frontage) == 1:
                # frontage is in ['A', 'B', ...
                letter_road = frontage
                clock_road = intersection
            else:
                letter_road = intersection
                clock_road = frontage

            d = {'value': camp['name'],
                 'clock_road': clock_road,
                 'letter_road': letter_road,
                 'id': camp['uid'],
                 'str_loc': obj_loc['string']
                 }
            filtered_list_of_camps.append(d)
    return json.dumps(filtered_list_of_camps[:30])

@app.route('/pan_to_camp/', methods=['POST'])
def pan_to_camp():
    name = request.form['value']
    clock_road = request.form['clock_road']
    letter_road = request.form['letter_road']
    print 'pan_to_camp', clock_road, letter_road

    camp = camp_to_man_xy(clock_road, letter_road)
    theta = lighthouse_camp_to_theta_degrees(camp)
    liblo.send(osc_server, '/staticLight/pan', theta)

    return flask.Response(status=204)

#@app.route("/pan_to_camp/<str:camp_name>/<camp_frontage>,<camp_intersection>")
#def pan_to_camp(camp_name, camp_frontage, camp_intersection):
#    return flask.Response(status=204)

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

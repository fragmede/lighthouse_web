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

from parse_camp_data import (
    parse_camp_location,
    filter_camp_list,
    )

app = Flask(__name__)
app.config['DEBUG'] = True

osc_server = liblo.Address('127.0.0.1', 8000)

@app.route("/")
def root():
    return flask.render_template('index.html')

@app.route("/camp_search/")
def camp_search():
    search_query = request.args.get('term')
    if not search_query:
        return json.dumps([])
    return json.dumps(filter_camp_list(search_query)[:30])

@app.route('/pan_to_camp/', methods=['POST'])
def pan_to_camp():
    name = request.form['value']
    uid = request.form['uid']

    location_info = location_from_camp_uid(uid)
    print location_info

    parsed_location_info = parse_camp_location(location_info)

    if 'man_x' in parsed_location_info:
        man_x = parsed_location_info['man_x']
        man_y = parsed_location_info['man_y']
        man_xy = (man_x, man_y)
    else:
        clock_road = parsed_location_info['clock_road']
        letter_road = parsed_location_info['letter_road']
        man_xy = camp_to_man_xy(clock_road, letter_road)

    theta = lighthouse_camp_to_theta_degrees(man_xy)
    liblo.send(osc_server, '/staticLight/pan', theta)

    print 'manxy', name, man_xy, theta

    return flask.Response(status=204)

@app.route('/pan_to_art/', methods=['POST'])
def pan_to_art():
    art_uid = request.form['uid']
    theta = parse_art_location(art)

    return flask.Response(status=204)

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

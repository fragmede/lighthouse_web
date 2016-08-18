#!/usr/bin/env python
import numpy as np
"""
Module to do math to translate city coords to man.

Esplanade is 2500 ft from man
E -> A is 400 ft
A -> B (and the rest) is 200 ft

using 'z' street for esplanade

Roads are 40 ft wide, split in half for each block.

Info from
http://burningman.org/event/black-rock-city-guide/2016-black-rock-city-plan/

"""

def hour_street_to_degrees_dist(hour,street_letter):
    if street_letter.lower() is 'z':
        return 2500
    dist = 2500 + 400 + ((ord(street_letter.lower()) - ord('a')) * 220)
    return hour_dist_to_degrees_dist(hour, dist)

def hour_dist_to_degrees_dist(hour, dist):
    degrees = hour * 30
    return degrees, dist

def degrees_dist_to_man_xy(degrees, dist):
    rad = np.radians(degrees)

    x = abs(dist * np.sin(rad))
    y = abs(dist * np.cos(rad))

    if degrees > 180: # 6 o'clock
        x = -x
    if 90 <= degrees <= 270: # 3 or 9 o'clock
        y = -y

    return np.array((x, y))

def lighthouse_hour_dist():
    """
    Lighthouse is (supposedly) at 11 o'clock and 2200 ft
    returns offset from man, X being 3 o'clock, y being 6 o'oclock
    """
    return 11, 2200

def lighthouse_man_xy():
    return art_to_man_xy(*lighthouse_hour_dist())

def art_to_man_xy(hour, dist):
    return degrees_dist_to_man_xy(*hour_dist_to_degrees_dist(hour, dist))

def camp_to_man_xy(hour, street_letter):
    return degrees_dist_to_man_xy(*hour_street_to_degrees_dist(hour, street_letter))

lh_xy = lighthouse_man_xy()
def lighthouse_camp_to_theta_degrees(camp_loc):
    xy_dist = camp_loc - lh_xy
    x_neg, y_neg = xy_dist[0] < 0, xy_dist[1] < 0

    raw_theta = np.degrees(np.arctan2(xy_dist[1], xy_dist[0]))
    return 180 - raw_theta

np.set_printoptions(precision=4, suppress=True)
nordic_space_camp = camp_to_man_xy(3, 'g')

#xy_dist = lh_xy + nordic_space_camp

#print lh_xy

camp = art_to_man_xy(0,0)
print '0  0 man should be 240', camp, lighthouse_camp_to_theta_degrees(camp)

camp = camp_to_man_xy(3,'e')
print '3  e should be 201', camp, lighthouse_camp_to_theta_degrees(camp)

camp = camp_to_man_xy(6,'e')
print '6 e expect 259', camp, lighthouse_camp_to_theta_degrees(camp)

camp = camp_to_man_xy(8,'l')
print '8  l expect 307', camp, lighthouse_camp_to_theta_degrees(camp)

camp = camp_to_man_xy(10,'b')
print '10  b expect 347', camp, lighthouse_camp_to_theta_degrees(camp)

camp = camp_to_man_xy(9,'c')
print '9  c expect 319', camp, lighthouse_camp_to_theta_degrees(camp)

camp = art_to_man_xy(11,2300)
print '11,2300 further past art on 11 o\'clock - expect 60', camp, lighthouse_camp_to_theta_degrees(camp)

camp = art_to_man_xy(12,2500)
print '12,2500 temple-ish - expect 151', camp, lighthouse_camp_to_theta_degrees(camp)


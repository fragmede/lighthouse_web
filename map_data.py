
import ujson as json

from map_to_lighthouse_pan_angle import (
    camp_to_man_xy,
    degrees_dist_to_man_xy,
    hour_dist_to_degrees_dist,
    raw_clock_to_decimal,
    )

camp_list = json.load(open('data/camp.2015.json'))

def is_only_time(s):
    for char in s:
        if char.isdigit():
            continue
        if char == ':':
            continue
        return False
    return True

def is_letter_road(s):
    if s == 'Esplanade':
        return True
    if len(s) == 1 and s.isalpha():
        return True
    return False

def handle_string_type(name):
    if is_only_time(name):
        return {'clock_road': name}
    elif is_letter_road(name):
        return {'letter_road': name}
    elif name == "Rod's Road":
        return {'_road': name}
    return None

def handle_intersection(intersection):
    rval = handle_string_type(intersection)
    if rval:
        return rval
    if intersection[-7:] == ' Portal':
        # Based on 2015 data, intersection is then
        # of the form 'ti:me Portal'
        return {'clock_road': intersection.split(' ')[0]}
    raise Exception('could not parse %s' % (intersection,))

def handle_frontage(frontage):
    rval = handle_string_type(frontage)
    if rval:
        return rval

    # I am guessing that 'portal' is man-side circle and plaza (and public
    # plaza) is mountain-side

    portal_postfix = ' Portal'
    if frontage[-len(portal_postfix):] == portal_postfix:
        # We are at a portal
        return {'clock_road': frontage.split(' ')[0], 'letter_road': 'b'}

    plaza_postfix = ' Plaza'
    if frontage[-len(plaza_postfix):] == plaza_postfix:
        # We are at a portal
        return {'clock_road': frontage.split(' ')[0], 'letter_road': 'b'}

    if frontage == "Rod's Road":
        # radius measured in road/blocks on map
        return {'portal_clock_road': '6:00', 'portal_clock_radius': 220 * 4}
    raise Exception('could not parse %s' % (frontage,))

def location_info_is_complete(loc):
    return 'clock_road' in loc and 'letter_road' in loc

def frontage_in_6_plaza(frontage):
    return frontage == "Rod's Road" or frontage == 'Center Camp Plaza'
    
def handle_6_plaza(frontage, intersection):
    if frontage == "Rod's Road":
        radius = 220 * 4
    else:
        radius = 220

    assert is_only_time(intersection)
    hour = raw_clock_to_decimal(intersection)
    if hour > 12:
        hour -= 12
    rod_x, rod_y = degrees_dist_to_man_xy(*hour_dist_to_degrees_dist(hour, radius))

    center_camp_center = '6:00', 'A'
    center_camp_man_x, center_camp_man_y = camp_to_man_xy(*center_camp_center)

    return {'man_x': center_camp_man_x + rod_x, 'man_y': center_camp_man_y + rod_y}

def parse_camp_location(loc):
    frontage = loc['frontage']
    intersection = loc['intersection']

    frontage_info = handle_frontage(frontage)

    if location_info_is_complete(frontage_info):
        return frontage_info

    intersection_info = handle_intersection(intersection)

    location_info = intersection_info.copy()
    location_info.update(frontage_info)

    if location_info_is_complete(location_info):
        return location_info

    if frontage_in_6_plaza(frontage):
        location_info = handle_6_plaza(frontage, intersection)
        return location_info

    raise Exception('yeah no. %s %s' % (frontage, intersection,) )

if __name__ == '__main__':
    for camp in camp_list:
        if not camp['location']['string']:
            continue
        location = parse_camp_location(camp)

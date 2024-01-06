# SPDX-FileCopyrightText: 2019-2023 Blender Foundation
#
# SPDX-License-Identifier: GPL-2.0-or-later

# --------------------------------------------------------------------------
# The sun positioning algorithms are based on the National Oceanic
# and Atmospheric Administration's (NOAA) Solar Position Calculator
# which rely on calculations of Jean Meeus' book "Astronomical Algorithms."
# Use of NOAA data and products are in the public domain and may be used
# freely by the public as outlined in their policies at
#               www.nws.noaa.gov/disclaimer.php
# --------------------------------------------------------------------------
# The geo parser script is by Maximilian Högner, released
# under the GNU GPL license:
# http://hoegners.de/Maxi/geo/
# --------------------------------------------------------------------------
# The addon which this code is based on is by Maximilian Högner and
# Damien Picard, released under the GPL-2.0-or-later license, on
# https://projects.blender.org/blender/blender-addons/src/branch/main/sun_position
# --------------------------------------------------------------------------

import bpy
from ark import utils
addon = utils.bpy.Addon()

# --------------------------------------------------------------------------
import re

class Parser:
    """ A parser class using regular expressions. """

    def __init__(self):
        self.patterns = {}
        self.raw_patterns = {}
        self.virtual = {}

    def add(self, name, pattern, virtual=False):
        """ Adds a new named pattern (regular expression) that can reference previously added patterns by %(pattern_name)s.
        Virtual patterns can be used to make expressions more compact but don't show up in the parse tree. """
        self.raw_patterns[name] = "(?:" + pattern + ")"
        self.virtual[name] = virtual

        try:
            self.patterns[name] = ("(?:" + pattern + ")") % self.patterns
        except KeyError as e:
            raise (Exception, "Unknown pattern name: %s" % str(e))

    def parse(self, pattern_name, text):
        """ Parses 'text' with pattern 'pattern_name' and returns parse tree """

        # build pattern with subgroups
        sub_dict = {}
        subpattern_names = []
        for s in re.finditer(r"%\(.*?\)s", self.raw_patterns[pattern_name]):
            subpattern_name = s.group()[2:-2]
            if not self.virtual[subpattern_name]:
                sub_dict[subpattern_name] = "(" + self.patterns[
                    subpattern_name] + ")"
                subpattern_names.append(subpattern_name)
            else:
                sub_dict[subpattern_name] = self.patterns[subpattern_name]

        pattern = "^" + (self.raw_patterns[pattern_name] % sub_dict) + "$"

        # do matching
        m = re.match(pattern, text)

        if m is None:
            return None

        # build tree recursively by parsing subgroups
        tree = {"TEXT": text}

        for i in range(len(subpattern_names)):
            text_part = m.group(i + 1)
            if text_part is not None:
                subpattern = subpattern_names[i]
                tree[subpattern] = self.parse(subpattern, text_part)

        return tree


position_parser = Parser()
position_parser.add("direction_ns", r"[NSns]")
position_parser.add("direction_ew", r"[EOWeow]")
position_parser.add("decimal_separator", r"[\.,]", True)
position_parser.add("sign", r"[+-]")

position_parser.add("nmea_style_degrees", r"[0-9]{2,}")
position_parser.add("nmea_style_minutes",
                    r"[0-9]{2}(?:%(decimal_separator)s[0-9]*)?")
position_parser.add(
    "nmea_style", r"%(sign)s?\s*%(nmea_style_degrees)s%(nmea_style_minutes)s")

position_parser.add(
    "number",
    r"[0-9]+(?:%(decimal_separator)s[0-9]*)?|%(decimal_separator)s[0-9]+")

position_parser.add("plain_degrees", r"(?:%(sign)s\s*)?%(number)s")

position_parser.add("degree_symbol", r"°", True)
position_parser.add("minutes_symbol", r"'|′|`|´", True)
position_parser.add("seconds_symbol",
                    r"%(minutes_symbol)s%(minutes_symbol)s|″|\"",
                    True)
position_parser.add("degrees", r"%(number)s\s*%(degree_symbol)s")
position_parser.add("minutes", r"%(number)s\s*%(minutes_symbol)s")
position_parser.add("seconds", r"%(number)s\s*%(seconds_symbol)s")
position_parser.add(
    "degree_coordinates",
    r"(?:%(sign)s\s*)?%(degrees)s(?:[+\s]*%(minutes)s)?(?:[+\s]*%(seconds)s)?|(?:%(sign)s\s*)%(minutes)s(?:[+\s]*%(seconds)s)?|(?:%(sign)s\s*)%(seconds)s"
)

position_parser.add(
    "coordinates_ns",
    r"%(nmea_style)s|%(plain_degrees)s|%(degree_coordinates)s")
position_parser.add(
    "coordinates_ew",
    r"%(nmea_style)s|%(plain_degrees)s|%(degree_coordinates)s")

position_parser.add(
    "position", (
        r"\s*%(direction_ns)s\s*%(coordinates_ns)s[,;\s]*%(direction_ew)s\s*%(coordinates_ew)s\s*|"
        r"\s*%(direction_ew)s\s*%(coordinates_ew)s[,;\s]*%(direction_ns)s\s*%(coordinates_ns)s\s*|"
        r"\s*%(coordinates_ns)s\s*%(direction_ns)s[,;\s]*%(coordinates_ew)s\s*%(direction_ew)s\s*|"
        r"\s*%(coordinates_ew)s\s*%(direction_ew)s[,;\s]*%(coordinates_ns)s\s*%(direction_ns)s\s*|"
        r"\s*%(coordinates_ns)s[,;\s]+%(coordinates_ew)s\s*"
    ))


def get_number(b):
    """ Takes appropriate branch of parse tree and returns float. """
    s = b["TEXT"].replace(",", ".")
    return float(s)


def get_coordinate(b):
    """ Takes appropriate branch of the parse tree and returns degrees as a float. """

    r = 0.

    if b.get("nmea_style"):
        if b["nmea_style"].get("nmea_style_degrees"):
            r += get_number(b["nmea_style"]["nmea_style_degrees"])
        if b["nmea_style"].get("nmea_style_minutes"):
            r += get_number(b["nmea_style"]["nmea_style_minutes"]) / 60.
        if b["nmea_style"].get(
                "sign") and b["nmea_style"]["sign"]["TEXT"] == "-":
            r *= -1.
    elif b.get("plain_degrees"):
        r += get_number(b["plain_degrees"]["number"])
        if b["plain_degrees"].get(
                "sign") and b["plain_degrees"]["sign"]["TEXT"] == "-":
            r *= -1.
    elif b.get("degree_coordinates"):
        if b["degree_coordinates"].get("degrees"):
            r += get_number(b["degree_coordinates"]["degrees"]["number"])
        if b["degree_coordinates"].get("minutes"):
            r += get_number(b["degree_coordinates"]["minutes"]["number"]) / 60.
        if b["degree_coordinates"].get("seconds"):
            r += get_number(
                b["degree_coordinates"]["seconds"]["number"]) / 3600.
        if b["degree_coordinates"].get(
                "sign") and b["degree_coordinates"]["sign"]["TEXT"] == "-":
            r *= -1.

    return r


def parse_position(s):
    """ Takes a (utf8-encoded) string describing a position and returns a tuple of floats for latitude and longitude in degrees.
    Tries to be as tolerant as possible with input. Returns None if parsing doesn't succeed. """

    parse_tree = position_parser.parse("position", s)
    if parse_tree is None:
        return None

    lat_sign = +1.
    if parse_tree.get(
            "direction_ns") and parse_tree["direction_ns"]["TEXT"] in ("S",
                                                                       "s"):
        lat_sign = -1.

    lon_sign = +1.
    if parse_tree.get(
            "direction_ew") and parse_tree["direction_ew"]["TEXT"] in ("W",
                                                                       "w"):
        lon_sign = -1.

    lat = lat_sign * get_coordinate(parse_tree["coordinates_ns"])
    lon = lon_sign * get_coordinate(parse_tree["coordinates_ew"])

    return lat, lon

# --------------------------------------------------------------------------

import datetime
TODAY = datetime.datetime.today()

# --------------------------------------------------------------------------

import datetime
from math import degrees, radians, pi, sin, cos, asin, acos, tan, floor

import mathutils

class SunInfo:
    """
    Store intermediate sun calculations
    """

    class SunBind:
        azimuth = 0.0
        elevation = 0.0
        az_start_sun = 0.0
        az_start_env = 0.0

    bind = SunBind()
    bind_to_sun = False

    latitude = 0.0
    longitude = 0.0
    elevation = 0.0
    azimuth = 0.0

    sunrise = 0.0
    sunset = 0.0

    month = 0
    day = 0
    year = 0
    day_of_year = 0
    time = 0.0

    UTC_zone = 0
    sun_distance = 0.0
    use_daylight_savings = False


sun = SunInfo()


def move_sun(context):
    """
    Cycle through all the selected objects and set their position and rotation
    in the sky.
    """
    addon_prefs = addon.preferences
    sun_props = context.scene.world.ark.sun_position

    if sun_props.usage_mode == "HDR":
        nt = context.scene.world.node_tree.nodes
        env_tex = nt.get(sun_props.hdr_texture)

        if sun.bind_to_sun != sun_props.bind_to_sun:
            # bind_to_sun was just toggled
            sun.bind_to_sun = sun_props.bind_to_sun
            sun.bind.az_start_sun = sun_props.hdr_azimuth
            if env_tex:
                sun.bind.az_start_env = env_tex.texture_mapping.rotation.z

        if env_tex and sun_props.bind_to_sun:
            az = sun_props.hdr_azimuth - sun.bind.az_start_sun + sun.bind.az_start_env
            env_tex.texture_mapping.rotation.z = az

        if sun_props.sun_object:
            obj = sun_props.sun_object
            obj.location = get_sun_vector(
                sun_props.hdr_azimuth, sun_props.hdr_elevation) * sun_props.sun_distance

            rotation_euler = mathutils.Euler((sun_props.hdr_elevation - pi/2,
                                    0, -sun_props.hdr_azimuth))

            set_sun_rotations(obj, rotation_euler)
        return

    local_time = sun_props.time
    zone = -sun_props.UTC_zone
    sun.use_daylight_savings = sun_props.use_daylight_savings
    if sun.use_daylight_savings:
        zone -= 1

    if addon_prefs.show_rise_set:
        calc_sunrise_sunset(rise=True)
        calc_sunrise_sunset(rise=False)

    azimuth, elevation = get_sun_coordinates(
        local_time, sun_props.latitude, sun_props.longitude,
        zone, sun_props.month, sun_props.day, sun_props.year)

    sun.azimuth = azimuth
    sun.elevation = elevation
    sun_vector = get_sun_vector(azimuth, elevation)

    if sun_props.sky_texture:
        sky_node = bpy.context.scene.world.node_tree.nodes.get(sun_props.sky_texture)
        if sky_node is not None and sky_node.type == "TEX_SKY":
            sky_node.texture_mapping.rotation.z = 0.0
            sky_node.sun_direction = sun_vector
            sky_node.sun_elevation = elevation
            sky_node.sun_rotation = azimuth

    # Sun object
    if (sun_props.sun_object is not None
            and sun_props.sun_object.name in context.view_layer.objects):
        obj = sun_props.sun_object
        obj.location = sun_vector * sun_props.sun_distance
        rotation_euler = mathutils.Euler((elevation - pi/2, 0, -azimuth))
        set_sun_rotations(obj, rotation_euler)

    # Sun collection
    if sun_props.object_collection is not None:
        sun_objects = sun_props.object_collection.objects
        object_count = len(sun_objects)
        if sun_props.object_collection_type == 'DIURNAL':
            # Diurnal motion
            if object_count > 1:
                time_increment = sun_props.time_spread / (object_count - 1)
                local_time = local_time + time_increment * (object_count - 1)
            else:
                time_increment = sun_props.time_spread

            for obj in sun_objects:
                azimuth, elevation = get_sun_coordinates(
                    local_time, sun_props.latitude,
                    sun_props.longitude, zone,
                    sun_props.month, sun_props.day)
                obj.location = get_sun_vector(azimuth, elevation) * sun_props.sun_distance
                local_time -= time_increment
                obj.rotation_euler = ((elevation - pi/2, 0, -azimuth))
        else:
            # Analemma
            day_increment = 365 / object_count
            day = sun_props.day_of_year + day_increment * (object_count - 1)
            for obj in sun_objects:
                dt = (datetime.date(sun_props.year, 1, 1) +
                      datetime.timedelta(day - 1))
                azimuth, elevation = get_sun_coordinates(
                    local_time, sun_props.latitude,
                    sun_props.longitude, zone,
                    dt.month, dt.day, sun_props.year)
                obj.location = get_sun_vector(azimuth, elevation) * sun_props.sun_distance
                day -= day_increment
                obj.rotation_euler = (elevation - pi/2, 0, -azimuth)


def day_of_year_to_month_day(year, day_of_year):
    dt = (datetime.date(year, 1, 1) + datetime.timedelta(day_of_year - 1))
    return dt.day, dt.month


def month_day_to_day_of_year(year, month, day):
    dt = datetime.date(year, month, day)
    return dt.timetuple().tm_yday


def update_time(context):
    sun_props = context.scene.world.ark.sun_position

    if sun_props.use_day_of_year:
        day, month = day_of_year_to_month_day(sun_props.year,
                                              sun_props.day_of_year)
        sun.day = day
        sun.month = month
        sun.day_of_year = sun_props.day_of_year
        if sun_props.day != day:
            sun_props.day = day
        if sun_props.month != month:
            sun_props.month = month
    else:
        day_of_year = month_day_to_day_of_year(
            sun_props.year, sun_props.month, sun_props.day)
        sun.day = sun_props.day
        sun.month = sun_props.month
        sun.day_of_year = day_of_year
        if sun_props.day_of_year != day_of_year:
            sun_props.day_of_year = day_of_year

    sun.year = sun_props.year
    sun.longitude = sun_props.longitude
    sun.latitude = sun_props.latitude
    sun.UTC_zone = sun_props.UTC_zone


@bpy.app.handlers.persistent
def sun_handler(scene):
    update_time(bpy.context)
    move_sun(bpy.context)


def format_time(time, daylight_savings, UTC_zone=None):
    if UTC_zone is not None:
        if daylight_savings:
            UTC_zone += 1
        time -= UTC_zone

    time %= 24

    return format_hms(time)


def format_hms(time):
    hh = int(time)
    mm = (time % 1.0) * 60
    ss = (mm % 1.0) * 60

    return f"{hh:02d}:{int(mm):02d}:{int(ss):02d}"


def format_lat_long(latitude, longitude):
    coordinates = ""

    for i, co in enumerate((latitude, longitude)):
        dd = abs(int(co))
        mm = abs(co - int(co)) * 60.0
        ss = abs(mm - int(mm)) * 60.0
        if co == 0:
            direction = ""
        elif i == 0:
            direction = "N" if co > 0 else "S"
        else:
            direction = "E" if co > 0 else "W"

        coordinates += f"{dd:02d}°{int(mm):02d}′{ss:05.2f}″{direction} "

    return coordinates.strip(" ")


def get_sun_coordinates(local_time, latitude, longitude,
                        utc_zone, month, day, year):
    """
    Calculate the actual position of the sun based on input parameters.

    The sun positioning algorithms below are based on the National Oceanic
    and Atmospheric Administration's (NOAA) Solar Position Calculator
    which rely on calculations of Jean Meeus' book "Astronomical Algorithms."
    Use of NOAA data and products are in the public domain and may be used
    freely by the public as outlined in their policies at
                www.nws.noaa.gov/disclaimer.php

    The calculations of this script can be verified with those of NOAA's
    using the Azimuth and Solar Elevation displayed in the SunPos_Panel.
    NOAA's web site is:
                http://www.esrl.noaa.gov/gmd/grad/solcalc
    """
    sun_props = bpy.context.scene.world.ark.sun_position

    longitude *= -1                   # for internal calculations
    utc_time = local_time + utc_zone  # Set Greenwich Meridian Time

    if latitude > 89.93:           # Latitude 90 and -90 gives
        latitude = radians(89.93)  # erroneous results so nudge it
    elif latitude < -89.93:
        latitude = radians(-89.93)
    else:
        latitude = radians(latitude)

    t = julian_time_from_y2k(utc_time, year, month, day)

    e = radians(obliquity_correction(t))
    L = apparent_longitude_of_sun(t)
    solar_dec = sun_declination(e, L)
    eqtime = calc_equation_of_time(t)

    time_correction = (eqtime - 4 * longitude) + 60 * utc_zone
    true_solar_time = ((utc_time - utc_zone) * 60.0 + time_correction) % 1440

    hour_angle = true_solar_time / 4.0 - 180.0
    if hour_angle < -180.0:
        hour_angle += 360.0

    csz = (sin(latitude) * sin(solar_dec) +
           cos(latitude) * cos(solar_dec) *
           cos(radians(hour_angle)))
    if csz > 1.0:
        csz = 1.0
    elif csz < -1.0:
        csz = -1.0

    zenith = acos(csz)

    az_denom = cos(latitude) * sin(zenith)

    if abs(az_denom) > 0.001:
        az_rad = ((sin(latitude) *
                  cos(zenith)) - sin(solar_dec)) / az_denom
        if abs(az_rad) > 1.0:
            az_rad = -1.0 if (az_rad < 0.0) else 1.0
        azimuth = pi - acos(az_rad)
        if hour_angle > 0.0:
            azimuth = -azimuth
    else:
        azimuth = pi if (latitude > 0.0) else 0.0

    if azimuth < 0.0:
        azimuth += 2*pi

    exoatm_elevation = 90.0 - degrees(zenith)

    if sun_props.use_refraction:
        if exoatm_elevation > 85.0:
            refraction_correction = 0.0
        else:
            te = tan(radians(exoatm_elevation))
            if exoatm_elevation > 5.0:
                refraction_correction = (
                    58.1 / te - 0.07 / (te ** 3) + 0.000086 / (te ** 5))
            elif exoatm_elevation > -0.575:
                s1 = -12.79 + exoatm_elevation * 0.711
                s2 = 103.4 + exoatm_elevation * s1
                s3 = -518.2 + exoatm_elevation * s2
                refraction_correction = 1735.0 + exoatm_elevation * (s3)
            else:
                refraction_correction = -20.774 / te

        refraction_correction /= 3600
        elevation = pi/2 - (zenith - radians(refraction_correction))

    else:
        elevation = pi/2 - zenith

    azimuth += sun_props.north_offset

    return azimuth, elevation


def get_sun_vector(azimuth, elevation):
    """
    Convert the sun coordinates to cartesian
    """
    phi = -azimuth
    theta = pi/2 - elevation

    loc_x = sin(phi) * sin(-theta)
    loc_y = sin(theta) * cos(phi)
    loc_z = cos(theta)
    return mathutils.Vector((loc_x, loc_y, loc_z))


def set_sun_rotations(obj, rotation_euler):
    rotation_quaternion = rotation_euler.to_quaternion()
    obj.rotation_quaternion = rotation_quaternion

    if obj.rotation_mode in {'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'}:
        obj.rotation_euler = rotation_quaternion.to_euler(obj.rotation_mode)
    else:
        obj.rotation_euler = rotation_euler

    rotation_axis_angle = obj.rotation_quaternion.to_axis_angle()
    obj.rotation_axis_angle = (rotation_axis_angle[1],
                               *rotation_axis_angle[0])


def calc_sunrise_set_UTC(rise, jd, latitude, longitude):
    t = calc_time_julian_cent(jd)
    eq_time = calc_equation_of_time(t)
    solar_dec = calc_sun_declination(t)
    hour_angle = calc_hour_angle_sunrise(latitude, solar_dec)
    if not rise:
        hour_angle = -hour_angle
    delta = longitude + degrees(hour_angle)
    time_UTC = 720 - (4.0 * delta) - eq_time
    return time_UTC


def calc_sun_declination(t):
    e = radians(obliquity_correction(t))
    L = apparent_longitude_of_sun(t)
    solar_dec = sun_declination(e, L)
    return solar_dec


def calc_hour_angle_sunrise(lat, solar_dec):
    lat_rad = radians(lat)
    HAarg = (cos(radians(90.833)) /
             (cos(lat_rad) * cos(solar_dec))
             - tan(lat_rad) * tan(solar_dec))
    if HAarg < -1.0:
        HAarg = -1.0
    elif HAarg > 1.0:
        HAarg = 1.0
    HA = acos(HAarg)
    return HA


def calc_sunrise_sunset(rise):
    zone = -sun.UTC_zone

    jd = get_julian_day(sun.year, sun.month, sun.day)
    time_UTC = calc_sunrise_set_UTC(rise, jd, sun.latitude, sun.longitude)
    new_time_UTC = calc_sunrise_set_UTC(rise, jd + time_UTC / 1440.0,
                                        sun.latitude, sun.longitude)
    time_local = new_time_UTC + (-zone * 60.0)
    tl = time_local / 60.0
    if sun.use_daylight_savings:
        time_local += 60.0
        tl = time_local / 60.0
    tl %= 24.0
    if rise:
        sun.sunrise = tl
    else:
        sun.sunset = tl


def julian_time_from_y2k(utc_time, year, month, day):
    """
    Get the elapsed julian time since 1/1/2000 12:00 gmt
    Y2k epoch (1/1/2000 12:00 gmt) is Julian day 2451545.0
    """
    century = 36525.0  # Days in Julian Century
    epoch = 2451545.0  # Julian Day for 1/1/2000 12:00 gmt
    jd = get_julian_day(year, month, day)
    return ((jd + (utc_time / 24)) - epoch) / century


def get_julian_day(year, month, day):
    if month <= 2:
        year -= 1
        month += 12
    A = floor(year / 100)
    B = 2 - A + floor(A / 4.0)
    jd = (floor((365.25 * (year + 4716.0))) +
          floor(30.6001 * (month + 1)) + day + B - 1524.5)
    return jd


def calc_time_julian_cent(jd):
    t = (jd - 2451545.0) / 36525.0
    return t


def sun_declination(e, L):
    return (asin(sin(e) * sin(L)))


def calc_equation_of_time(t):
    epsilon = obliquity_correction(t)
    ml = radians(mean_longitude_sun(t))
    e = eccentricity_earth_orbit(t)
    m = radians(mean_anomaly_sun(t))
    y = tan(radians(epsilon) / 2.0)
    y = y * y
    sin2ml = sin(2.0 * ml)
    cos2ml = cos(2.0 * ml)
    sin4ml = sin(4.0 * ml)
    sinm = sin(m)
    sin2m = sin(2.0 * m)
    etime = (y * sin2ml - 2.0 * e * sinm + 4.0 * e * y *
             sinm * cos2ml - 0.5 * y ** 2 * sin4ml - 1.25 * e ** 2 * sin2m)
    return (degrees(etime) * 4)


def obliquity_correction(t):
    ec = obliquity_of_ecliptic(t)
    omega = 125.04 - 1934.136 * t
    return (ec + 0.00256 * cos(radians(omega)))


def obliquity_of_ecliptic(t):
    return ((23.0 + 26.0 / 60 + (21.4480 - 46.8150) / 3600 * t -
             (0.00059 / 3600) * t**2 + (0.001813 / 3600) * t**3))


def true_longitude_of_sun(t):
    return (mean_longitude_sun(t) + equation_of_sun_center(t))


def calc_sun_apparent_long(t):
    o = true_longitude_of_sun(t)
    omega = 125.04 - 1934.136 * t
    lamb = o - 0.00569 - 0.00478 * sin(radians(omega))
    return lamb


def apparent_longitude_of_sun(t):
    return (radians(true_longitude_of_sun(t) - 0.00569 - 0.00478 *
            sin(radians(125.04 - 1934.136 * t))))


def mean_longitude_sun(t):
    return (280.46646 + 36000.76983 * t + 0.0003032 * t**2) % 360


def equation_of_sun_center(t):
    m = radians(mean_anomaly_sun(t))
    c = ((1.914602 - 0.004817 * t - 0.000014 * t**2) * sin(m) +
         (0.019993 - 0.000101 * t) * sin(m * 2) +
         0.000289 * sin(m * 3))
    return c


def mean_anomaly_sun(t):
    return (357.52911 + t * (35999.05029 - 0.0001537 * t))


def eccentricity_earth_orbit(t):
    return (0.016708634 - 0.000042037 * t - 0.0000001267 * t ** 2)


def calc_surface(context):
    coords = []
    sun_props = context.scene.world.ark.sun_position
    zone = -sun_props.UTC_zone

    def get_surface_coordinates(time, month):
        azimuth, elevation = get_sun_coordinates(
            time, sun_props.latitude, sun_props.longitude,
            zone, month, 1, sun_props.year)
        sun_vector = get_sun_vector(azimuth, elevation) * sun_props.sun_distance
        sun_vector.z = max(0, sun_vector.z)
        return sun_vector

    for month in range(1, 7):
        for time in range(24):
            coords.append(get_surface_coordinates(time, month))
            coords.append(get_surface_coordinates(time + 1, month))
            coords.append(get_surface_coordinates(time, month + 1))

            coords.append(get_surface_coordinates(time, month + 1))
            coords.append(get_surface_coordinates(time + 1, month + 1))
            coords.append(get_surface_coordinates(time + 1, month))
    return coords


def calc_analemma(context, h):
    vertices = []
    sun_props = context.scene.world.ark.sun_position
    zone = -sun_props.UTC_zone
    for day_of_year in range(1, 367, 5):
        day, month = day_of_year_to_month_day(sun_props.year, day_of_year)
        azimuth, elevation = get_sun_coordinates(
            h, sun_props.latitude, sun_props.longitude,
            zone, month, day, sun_props.year)
        sun_vector = get_sun_vector(azimuth, elevation) * sun_props.sun_distance
        if sun_vector.z > 0:
            vertices.append(sun_vector)
    return vertices

# --------------------------------------------------------------------------

import bpy
import math
import gpu
from gpu_extras.batch import batch_for_shader

if bpy.app.background:  # ignore drawing in background mode
    def north_update(self, context):
        pass
    def surface_update(self, context):
        pass
    def analemmas_update(self, context):
        pass
else:
    # North line

    shader_interface = gpu.types.GPUStageInterfaceInfo("my_interface")
    shader_interface.flat('VEC2', "v_StartPos")
    shader_interface.smooth('VEC4', "v_VertPos")

    shader_info = gpu.types.GPUShaderCreateInfo()
    shader_info.push_constant('MAT4', "u_ViewProjectionMatrix")
    shader_info.push_constant('VEC4', "u_Color")
    shader_info.push_constant('VEC2', "u_Resolution")
    shader_info.vertex_in(0, 'VEC3', "position")
    shader_info.vertex_out(shader_interface)

    shader_info.vertex_source(
        '''
        void main()
        {
            vec4 pos    = u_ViewProjectionMatrix * vec4(position, 1.0f);
            gl_Position = pos;
            v_StartPos    = (pos / pos.w).xy;
            v_VertPos     = pos;
        }
        '''
    )

    shader_info.fragment_out(0, 'VEC4', "FragColor")
    shader_info.fragment_source(
        '''
        void main()
        {
            vec4 vertPos_2d = v_VertPos / v_VertPos.w;
            vec2 dir  = (vertPos_2d.xy - v_StartPos.xy) * u_Resolution;
            float dist = length(dir);

            if (step(sin(dist / 5.0f), 0.0) == 1) discard;

            FragColor = u_Color;
        }
        '''
    )

    shader = gpu.shader.create_from_info(shader_info)
    del shader_info
    del shader_interface

    def north_draw():
        """
        Set up the compass needle using the current north offset angle
        less 90 degrees.  This forces the unit circle to begin at the
        12 O'clock instead of 3 O'clock position.
        """
        sun_props = bpy.context.scene.world.ark.sun_position

        color = (0.2, 0.6, 1.0, 0.7)
        radius = 100
        angle = -(sun_props.north_offset - math.pi / 2)
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        coords = mathutils.Vector((x, y, 0)), mathutils.Vector((0, 0, 0))
        batch = batch_for_shader(shader, 'LINE_STRIP', {"position": coords})

        matrix = bpy.context.region_data.perspective_matrix
        shader.uniform_float("u_ViewProjectionMatrix", matrix)
        shader.uniform_float("u_Resolution", (bpy.context.region.width,
                                              bpy.context.region.height))
        shader.uniform_float("u_Color", color)
        width = gpu.state.line_width_get()
        gpu.state.line_width_set(2.0)
        batch.draw(shader)
        gpu.state.line_width_set(width)

    _north_handle = None

    def north_update(self, context):
        global _north_handle
        sun_props = context.scene.world.ark.sun_position
        addon_prefs = addon.preferences

        if addon_prefs.show_overlays and sun_props.show_north:
            if _north_handle is None:
                _north_handle = bpy.types.SpaceView3D.draw_handler_add(north_draw, (), 'WINDOW', 'POST_VIEW')
        elif _north_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(_north_handle, 'WINDOW')
            _north_handle = None

    # Analemmas

    def analemmas_draw(batch, shader):
        shader.uniform_float("color", (1, 0, 0, 1))
        batch.draw(shader)

    _analemmas_handle = None

    def analemmas_update(self, context):
        global _analemmas_handle
        sun_props = context.scene.world.ark.sun_position
        addon_prefs = addon.preferences

        if addon_prefs.show_overlays and sun_props.show_analemmas:
            coords = []
            indices = []
            coord_offset = 0
            for h in range(24):
                analemma_verts = calc_analemma(context, h)
                coords.extend(analemma_verts)
                for i in range(len(analemma_verts) - 1):
                    indices.append((coord_offset + i,
                                    coord_offset + i+1))
                coord_offset += len(analemma_verts)

            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES',
                                    {"pos": coords}, indices=indices)

            if _analemmas_handle is not None:
                bpy.types.SpaceView3D.draw_handler_remove(_analemmas_handle, 'WINDOW')
            _analemmas_handle = bpy.types.SpaceView3D.draw_handler_add(
                analemmas_draw, (batch, shader), 'WINDOW', 'POST_VIEW')
        elif _analemmas_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(_analemmas_handle, 'WINDOW')
            _analemmas_handle = None

    # Surface

    def surface_draw(batch, shader):
        blend = gpu.state.blend_get()
        gpu.state.blend_set("ALPHA")
        shader.uniform_float("color", (.8, .6, 0, 0.2))
        batch.draw(shader)
        gpu.state.blend_set(blend)

    _surface_handle = None

    def surface_update(self, context):
        global _surface_handle
        sun_props = context.scene.world.ark.sun_position
        addon_prefs = addon.preferences

        if addon_prefs.show_overlays and sun_props.show_surface:
            coords = calc_surface(context)
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'TRIS', {"pos": coords})

            if _surface_handle is not None:
                bpy.types.SpaceView3D.draw_handler_remove(_surface_handle, 'WINDOW')
            _surface_handle = bpy.types.SpaceView3D.draw_handler_add(
                surface_draw, (batch, shader), 'WINDOW', 'POST_VIEW')
        elif _surface_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(_surface_handle, 'WINDOW')
            _surface_handle = None

# --------------------------------------------------------------------------

class ARK_OT_SunPositionPasteGMaps(bpy.types.Operator):
    bl_idname = f"{addon.name}.sunposition_paste_gmaps"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    def execute(self, context):
        link = bpy.context.window_manager.clipboard
        m = re.search(r"@([-\d\.]+),([-\d\.]+)", link)
        if m is None:
            self.report({'ERROR'}, "Invalid Google Maps link.")
            return {'CANCELLED'}
        else:
            latitude, longitude = m.groups()
            pr_world = getattr(context.scene.world, addon.name)
            pr_world.sun_position.latitude = float(latitude)
            pr_world.sun_position.longitude = float(longitude)
            return {'FINISHED'}

class ARK_OT_SunPositionOpenGMaps(bpy.types.Operator):
    bl_idname = f"{addon.name}.sunposition_open_gmaps"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    def execute(self, context):
        pr_world = getattr(context.scene.world, addon.name)
        print(f"https://www.google.com/maps/place/{pr_world.sun_position.coordinates}")

        # https://www.google.com/maps/place/42°08'20.6"N+19°18'18.9"W/
        bpy.ops.wm.url_open(url=f"https://www.google.com/maps/place/{pr_world.sun_position.coordinates}")
        return {'INTERFACE'}

# --------------------------------------------------------------------------

parse_success = True


def lat_long_update(self, context):
    global parse_success
    parse_success = True
    sun_update(self, context)


def get_coordinates(self):
    if parse_success:
        return format_lat_long(self.latitude, self.longitude)
    return iface_("ERROR: Could not parse coordinates")


def set_coordinates(self, value):
    parsed_co = parse_position(value)

    global parse_success
    if parsed_co is not None and len(parsed_co) == 2:
        latitude, longitude = parsed_co
        self.latitude, self.longitude = latitude, longitude
    else:
        parse_success = False

    sun_update(self, bpy.context)


def sun_update(self, context):
    sun_props = context.scene.world.ark.sun_position

    update_time(context)
    move_sun(context)

    if sun_props.show_surface:
        surface_update(self, context)
    if sun_props.show_analemmas:
        analemmas_update(self, context)
    if sun_props.show_north:
        north_update(self, context)


class World_SunPosition(bpy.types.PropertyGroup):
    usage_mode: bpy.props.EnumProperty(
        name="Usage Mode",
        description="Operate in normal mode or environment texture mode",
        items=(
            ('NORMAL', "Normal", ""),
            ('HDR', "Sun + HDR texture", ""),
        ),
        default='NORMAL',
        update=sun_update)

    use_daylight_savings: bpy.props.BoolProperty(
        name="Daylight Savings",
        description="Daylight savings time adds 1 hour to standard time",
        default=False,
        update=sun_update)

    use_refraction: bpy.props.BoolProperty(
        name="Use Refraction",
        description="Show the apparent Sun position due to atmospheric refraction",
        default=True,
        update=sun_update)

    show_north: bpy.props.BoolProperty(
        name="Show North",
        description="Draw a line pointing to the north",
        default=False,
        update=north_update)

    north_offset: bpy.props.FloatProperty(
        name="North Offset",
        description="Rotate the scene to choose the North direction",
        unit="ROTATION",
        soft_min=-pi, soft_max=pi, step=10.0, default=0.0,
        update=sun_update)

    show_surface: bpy.props.BoolProperty(
        name="Show Surface",
        description="Draw the surface that the Sun occupies in the sky",
        default=False,
        update=surface_update)

    show_analemmas: bpy.props.BoolProperty(
        name="Show Analemmas",
        description="Draw Sun analemmas. These help visualize the motion of the Sun in the sky during the year, for each hour of the day",
        default=False,
        update=analemmas_update)

    coordinates: bpy.props.StringProperty(
        name="Coordinates [WGS84]",
        description="Enter coordinates from an online map",
        get=get_coordinates,
        set=set_coordinates,
        default="00°00′00.00″ 00°00′00.00″",
        options={'SKIP_SAVE'})

    latitude: bpy.props.FloatProperty(
        name="Latitude",
        description="Latitude: (+) Northern (-) Southern",
        soft_min=-90.0, soft_max=90.0,
        step=5, precision=3,
        default=0.0,
        update=lat_long_update)

    longitude: bpy.props.FloatProperty(
        name="Longitude",
        description="Longitude: (-) West of Greenwich (+) East of Greenwich",
        soft_min=-180.0, soft_max=180.0,
        step=5, precision=3,
        default=0.0,
        update=lat_long_update)

    sunrise_time: bpy.props.FloatProperty(
        name="Sunrise Time",
        description="Time at which the Sun rises",
        soft_min=0.0, soft_max=24.0,
        default=0.0,
        get=lambda _: sun.sunrise)

    sunset_time: bpy.props.FloatProperty(
        name="Sunset Time",
        description="Time at which the Sun sets",
        soft_min=0.0, soft_max=24.0,
        default=0.0,
        get=lambda _: sun.sunset)

    sun_elevation: bpy.props.FloatProperty(
        name="Sun Elevation",
        description="Elevation angle of the Sun",
        soft_min=-pi/2, soft_max=pi/2,
        precision=3,
        default=0.0,
        unit="ROTATION",
        get=lambda _: sun.elevation)

    sun_azimuth: bpy.props.FloatProperty(
        name="Sun Azimuth",
        description="Rotation angle of the Sun from the direction of the north",
        soft_min=-pi, soft_max=pi,
        precision=3,
        default=0.0,
        unit="ROTATION",
        get=lambda _: sun.azimuth - bpy.context.scene.world.ark.sun_position.north_offset)

    month: bpy.props.IntProperty(
        name="Month",
        min=1, max=12, default=TODAY.month,
        update=sun_update)

    day: bpy.props.IntProperty(
        name="Day",
        min=1, max=31, default=TODAY.day,
        update=sun_update)

    year: bpy.props.IntProperty(
        name="Year",
        min=1, max=4000, default=TODAY.year,
        update=sun_update)

    use_day_of_year: bpy.props.BoolProperty(
        description="Use a single value for the day of year",
        name="Use day of year",
        default=False,
        update=sun_update)

    day_of_year: bpy.props.IntProperty(
        name="Day of Year",
        min=1, max=366, default=1,
        update=sun_update)

    UTC_zone: bpy.props.FloatProperty(
        name="UTC Zone",
        description="Difference from Greenwich, England, in hours",
        precision=1,
        min=-14.0, max=13, step=50, default=0.0,
        update=sun_update)

    time: bpy.props.FloatProperty(
        name="Time",
        description="Time of the day",
        precision=4,
        soft_min=0.0, soft_max=23.9999, step=1.0, default=12.0,
        update=sun_update)

    sun_distance: bpy.props.FloatProperty(
        name="Distance",
        description="Distance to the Sun from the origin",
        unit="LENGTH",
        min=0.0, soft_max=3000.0, step=10.0, default=50.0,
        update=sun_update)

    sun_object: bpy.props.PointerProperty(
        name="Sun Object",
        type=bpy.types.Object,
        description="Sun object to use in the scene",
        poll=lambda self, obj: obj.type == 'LIGHT',
        update=sun_update)

    object_collection: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection,
        description="Collection of objects used to visualize the motion of the Sun",
        update=sun_update)

    object_collection_type: bpy.props.EnumProperty(
        name="Display type",
        description="Type of Sun motion to visualize",
        items=(
            ('ANALEMMA', "Analemma", "Trajectory of the Sun in the sky during the year, for a given time of the day"),
            ('DIURNAL', "Diurnal", "Trajectory of the Sun in the sky during a single day"),
        ),
        default='ANALEMMA',
        update=sun_update)

    sky_texture: bpy.props.StringProperty(
        name="Sky Texture",
        default="",
        description="Name of the sky texture to use",
        update=sun_update)

    hdr_texture: bpy.props.StringProperty(
        default="Environment Texture",
        name="Environment Texture",
        description="Name of the environment texture to use. World nodes must be enabled "
                    "and the color set to an environment Texture",
        update=sun_update)

    hdr_azimuth: bpy.props.FloatProperty(
        name="Rotation",
        description="Rotation angle of the Sun and environment texture",
        unit="ROTATION",
        step=10.0,
        default=0.0, precision=3,
        update=sun_update)

    hdr_elevation: bpy.props.FloatProperty(
        name="Elevation",
        description="Elevation angle of the Sun",
        unit="ROTATION",
        step=10.0,
        default=0.0, precision=3,
        update=sun_update)

    bind_to_sun: bpy.props.BoolProperty(
        name="Bind Texture to Sun",
        description="If enabled, the environment texture moves with the Sun",
        default=False,
        update=sun_update)

    time_spread: bpy.props.FloatProperty(
        name="Time Spread",
        description="Time period around which to spread object collection",
        precision=4,
        soft_min=1.0, soft_max=24.0, step=1.0, default=23.0,
        update=sun_update)

@addon.property
class Preferences_Worlds_SunPosition(bpy.types.PropertyGroup):
    show_overlays: bpy.props.BoolProperty(
        name="Show Overlays",
        description="Display overlays in the viewport: the direction of the north, analemmas and the Sun surface",
        default=True,
        update=sun_update
    )

    show_refraction: bpy.props.BoolProperty(
        name="Refraction",
        description="Show Sun Refraction choice",
        default=False
    )

    show_az_el: bpy.props.BoolProperty(
        name="Azimuth and Elevation Info",
        description="Show azimuth and solar elevation info",
        default=True
    )

    show_rise_set: bpy.props.BoolProperty(
        name="Sunrise and Sunset Info",
        description="Show sunrise and sunset labels",
        default=True
    )

def UI(preferences, layout):
    split = layout.row(align=True).split(factor=0.245)
    split.label(text="Overlays")
    col = split.column()
    col.label(text="")
    col.prop(preferences, "show_overlays", toggle=True)
    col.prop(preferences, "show_refraction", toggle=True)
    col.prop(preferences, "show_az_el", toggle=True)
    col.prop(preferences, "show_rise_set", toggle=True)
    return None

CLASSES = [
    ARK_OT_SunPositionPasteGMaps,
    ARK_OT_SunPositionOpenGMaps,
    World_SunPosition,
    Preferences_Worlds_SunPosition,
]

PROPS = [
    World_SunPosition,
]

def register():
    utils.bpy.register_classes(CLASSES)
    addon.set_properties(PROPS)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
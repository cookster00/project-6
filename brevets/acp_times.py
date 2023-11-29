"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_acp.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow
import math


# Create dictionaries for the specified time and location values
span1 = {'start_dist': 0, 'end_dist': 200, 'min_speed': 15, 'max_speed': 34}
span2 = {'start_dist': 200, 'end_dist': 400, 'min_speed': 15, 'max_speed': 32}
span3 = {'start_dist': 400, 'end_dist': 600, 'min_speed': 15, 'max_speed': 30}
span4 = {'start_dist': 600, 'end_dist': 1000, 'min_speed': 11.428, 'max_speed': 28}


def control_calc(control, speed):
    raw_time = control / speed
    hour = math.floor(raw_time)
    frac_minutes = raw_time - hour
    minute = round(frac_minutes * 60)
    return_val = {'hour': hour, 'minute': minute}
    return raw_time


def convert_to_hm(raw_time):
    hour = math.floor(raw_time)
    frac_minutes = raw_time - hour
    minute = round(frac_minutes * 60)
    return_val = {'hour': hour, 'minute': minute}
    return return_val


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
        control_dist_km:  number, control distance in kilometers
        brevet_dist_km: number, nominal distance of the brevet
            in kilometers, which must be one of 200, 300, 400, 600,
            or 1000 (the only official ACP brevet distances)
        brevet_start_time:  An arrow object
    Returns:
        An arrow object indicating the control open time.
        This will be in the same time zone as the brevet start time.
    """
    time = arrow.get(brevet_start_time)
    hour = 0
    minute = 0

    # if the control is longer than the brevet, the calculation should be with brevet instead
    if control_dist_km > brevet_dist_km:
        control = brevet_dist_km
    else:
        control = control_dist_km

    if control <= 200:
        raw_time = control_calc(control, control_0_2['max_speed'])
        time_result = convert_to_hm(raw_time)
        hour = time_result['hour']
        minute = time_result['minute']
    elif control <= 400:
        # calculate when distance is <=200
        raw_time_1 = control_calc(200, span1['max_speed'])

        # calculate when distance is >200
        remain_control_dist = control - 200
        raw_time_2 = control_calc(remain_control_dist, span2['max_speed'])

        total_raw_time = raw_time_1 + raw_time_2
        time_result = convert_to_hm(total_raw_time)

        hour = time_result['hour']
        minute = time_result['minute']
    elif control <= 600:
        # calculate when distance is <=200
        raw_time_1 = control_calc(200, span1['max_speed'])

        # calculate when distance is <=400
        raw_time_2 = control_calc(200, span2['max_speed'])

        # calculate remaining distance with new start time
        remain_control_dist = control - 400
        raw_time_3 = control_calc(remain_control_dist, span3['max_speed'])

        total_raw_time = raw_time_1 + raw_time_2 + raw_time_3
        time_result = convert_to_hm(total_raw_time)

        hour = time_result['hour']
        minute = time_result['minute']
    elif control <= 1000:
        # calculate when distance is <=200
        raw_time_1 = control_calc(200, span1['max_speed'])

        # calculate when distance is <=400
        raw_time_2 = control_calc(200, span2['max_speed'])

        # calculate when distance is <=600
        raw_time_3 = control_calc(200, span3['max_speed'])

        # calculate remaining distance
        remain_control_dist = control - 600
        raw_time_4 = control_calc(remain_control_dist, span4['max_speed'])

        total_raw_time = raw_time_1 + raw_time_2 + raw_time_3 + raw_time_4
        time_result = convert_to_hm(total_raw_time)

        hour = time_result['hour']
        minute = time_result['minute']

    start_time = time.shift(hours=hour, minutes=minute)
    return start_time


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
        control_dist_km:  number, control distance in kilometers
        brevet_dist_km: number, nominal distance of the brevet
        in kilometers, which must be one of 200, 300, 400, 600, or 1000
        (the only official ACP brevet distances)
        brevet_start_time:  An arrow object
    Returns:
        An arrow object indicating the control close time.
        This will be in the same time zone as the brevet start time.
    """
    time = arrow.get(brevet_start_time)
    hour = 0
    minute = 0

    # if the control is longer than the brevet, the calculation should be with brevet instead
    if control_dist_km > brevet_dist_km:
        control = brevet_dist_km
    else:
        control = control_dist_km

    # if the control is 0, close time should be 1hr
    if control == 0:
        hour = 1
    elif control <= 60:
        total_raw_time = control_calc(control, 20)
        time_result = convert_to_hm(total_raw_time)

        hour = time_result['hour'] + 1
        minute = time_result['minute']
    # time limits for races
    elif control == 200 and brevet_dist_km == 200:
        hour = 13
        minute = 30
    elif control == 300 and brevet_dist_km == 300:
        hour = 20
        minute = 0
    elif control == 400 and brevet_dist_km == 400:
        hour = 27
        minute = 0
    elif control == 600 and brevet_dist_km == 600:
        hour = 40
        minute = 0
    elif control == 1000 and brevet_dist_km == 1000:
        hour = 75
        minute = 0

    elif control <= 600:
        total_raw_time = control_calc(control, span1['min_speed'])
        time_result = convert_to_hm(total_raw_time)

        hour = time_result['hour']
       

"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_acp.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

# Initializing global variables of each distance span with the following information included:
#   start_dist -> beginning of distance span
#   end_dist -> end of distance span
#   max_speed -> maximum speed a rider is allowed to bike within given span
#   min_speed -> minimum speed a rider is allowed to bike within given span
dist_span_1 = {'start_dist': 0, 'end_dist': 200, 'max_speed': 34, 'min_speed': 15}
dist_span_2 = {'start_dist': 200, 'end_dist': 400, 'max_speed': 32, 'min_speed': 15}
dist_span_3 = {'start_dist': 400, 'end_dist': 600, 'max_speed': 30, 'min_speed': 15}
dist_span_4 = {'start_dist': 600, 'end_dist': 1000, 'max_speed': 28, 'min_speed': 11.428}

# Initializing global variable of a list of all distance spans
dist_spans = [dist_span_1, dist_span_2, dist_span_3, dist_span_4]

def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, control distance in kilometers // Spot of checkpoint
       brevet_dist_km: number, nominal distance of the brevet   // Overall distance of the race
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An arrow object                      // when the race starts
    Returns:
       An arrow object indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    brevet_start_time = arrow.get(brevet_start_time)
    # Checking for special cases
    if control_dist_km < 0:
        # if control distance is negative then raise error
        raise ValueError
    elif control_dist_km == 0:
        # control distance = 0, start time is opening time
        return brevet_start_time
    elif control_dist_km > int(brevet_dist_km):
        # if control gate is further than the end of the race, set it equal to brevet distance
        control_dist_km = int(brevet_dist_km)

    control_open_time = brevet_start_time
    minute_shift = 0
    
    for dist_span in dist_spans:
        # if control checkpoint is within dist_span
        if dist_span['start_dist'] < control_dist_km <= dist_span['end_dist']:          
            # calculate time from start of span to checkpoint if rider is moving at min_speed
            fastest_time_to_control = (control_dist_km - dist_span['start_dist']) / dist_span['max_speed']

            # Add to minute_shift
            minute_shift += fastest_time_to_control * 60
            break
        
        # If control_distance not in dist_span
        else:
            # get total time to ride dist_span at max_speed and add to minute_shift
            added_time = (dist_span['end_dist'] - dist_span['start_dist']) / dist_span['max_speed']
            minute_shift += added_time * 60


    control_open_time = control_open_time.shift(minutes=+round(minute_shift))
    return control_open_time


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
    brevet_start_time = arrow.get(brevet_start_time)
    # check for special cases
    if control_dist_km < 0:
        raise ValueError
    elif control_dist_km == 0:
        # if control distance is 0: close time is 60
        return brevet_start_time.shift(minutes=+60)
    elif control_dist_km <= 60:
        # if control is within 60 km of start: special case
        minute_shift = round((control_dist_km / 20) * 60 + 60)
        return brevet_start_time.shift(minutes=+minute_shift)
    elif control_dist_km >= int(brevet_dist_km):
        # if control distance 
        control_dist_km = int(brevet_dist_km)

    control_close_time = brevet_start_time
    minute_shift = 0

    for dist_span in dist_spans:
        if dist_span['start_dist'] < control_dist_km <= dist_span['end_dist']:
            
            slowest_time_to_control = (control_dist_km - dist_span['start_dist']) / dist_span['min_speed']
            minute_shift += slowest_time_to_control * 60
            break
        else:
            added_time = (dist_span['end_dist'] - dist_span['start_dist']) / dist_span['min_speed']
            minute_shift += added_time * 60

    control_close_time = control_close_time.shift(minutes=+round(minute_shift))
    return control_close_time

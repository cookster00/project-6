"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_acp.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

# Initializing global variables of each distance span with the following information included:
#   start_dist -> beginning of distance 
#   end_dist -> ending distance
#   max_speed -> maximum speed a rider is allowed to bike
#   min_speed -> minimum speed a rider is allowed to bike 
#   quickest -> amount of time it would take to ride span from front to end at max speed.
#       Format: [hours, minutes]
#   slowest -> amount of time it would take to ride span from front to end at minimum speed.
#       Format: [hours, minutes]
span1 = {'start_dist': 0, 'end_dist': 200, 'max_speed': 34, 'min_speed': 15}
span2 = {'start_dist': 200, 'end_dist': 400, 'max_speed': 32, 'min_speed': 15}
span3 = {'start_dist': 400, 'end_dist': 600, 'max_speed': 30, 'min_speed': 15}
span4 = {'start_dist': 600, 'end_dist': 1000, 'max_speed': 28, 'min_speed': 11.428}

# Initializing global variable of a list of all distance spans
dist_spans = [span1, span2, span3, span4]

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

    if control_dist_km < 0:
        # control distance is neg
        raise ValueError
    elif control_dist_km == 0:
        # control distance is 0
        return brevet_start_time
    elif control_dist_km > int(brevet_dist_km):
        control_dist_km = int(brevet_dist_km)

    control_open_time = brevet_start_time
    hour_shift = 0
    minute_shift = 0
    log = ""

    for dist_span in dist_spans:
        # if the control checkpoint is within the selected distance span, then begin to calculate using information from dist_span
        if dist_span['start_dist'] < control_dist_km <= dist_span['end_dist']:
            log += "entering if with control_open_time = {}".format(control_open_time)
            # Calculates the time to checkpoint if rider is moving at max speed (aka the controls opening time):
            fastest = (control_dist_km - dist_span['start_dist']) / dist_span['max_speed']

            # Seperating fastest_time_to_control into hours and minutes that it takes
            minute_shift += fastest * 60

            # Got to the given checkpoint and can return overall time now
            break
        
        # If the control distance is not within this distance span, add the total_quickest_time of the span to account for distance, and then we can re-enter loop
        else:
            log += "entering else with control_open_time = {}".format(control_open_time)
            added = (dist_span['end_dist'] - dist_span['start_dist']) / dist_span['max_speed']
            minute_shift += added * 60
            log += "exiting else with control_open_time = {}".format(control_open_time)
    
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
    
    
    if control_dist_km < 0:
        # control distance is neg
        raise ValueError
    elif control_dist_km == 0: 
        # control distance is 0
        return brevet_start_time.shift(minutes=+60)
    elif control_dist_km <= 60: 
        # special timing for gate closure when gate within 60km of start
        minute_shift = round((control_dist_km/20) * 60 + 60)
        return brevet_start_time.shift(minutes=+minute_shift)
    elif control_dist_km >= int(brevet_dist_km):
        control_dist_km = int(brevet_dist_km)

    control_close_time = brevet_start_time
    hour_shift = 0
    minute_shift = 0

    for dist_span in dist_spans:
        if dist_span['start_dist'] < control_dist_km <= dist_span['end_dist']:
            slowest = (control_dist_km - dist_span['start_dist']) / dist_span['min_speed']

            minute_shift += slowest * 60
            break
        else:
            added = (dist_span['end_dist'] - dist_span['start_dist']) / dist_span['min_speed']
            minute_shift += added * 60
        
    control_close_time = control_close_time.shift(minutes=+round(minute_shift))
    return control_close_time

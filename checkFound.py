import requests

def checkJSON(flight, filters):
    # Apply all filters
    for key, filter_config in filters.get('filters', {}).items():
        # Skip the filter if the flight doesn't have the key
        if key != "pos" and key not in flight:
            continue

        # Special case for position
        if key == "pos":
            lat = flight.get("lat")
            lon = flight.get("lon")
            if lat is not None and lon is not None:
                if not checkFilterPos(filter_config, lat, lon):
                    return [False, None, None, None]
            # If lat/lon missing, skip position check
        else:
            value = flight.get(key)
            if value is not None and not checkFilter(filter_config, value):
                return [False, None, None, None]

    # If passed all applicable filters, format notification
    title = formatMsg(filters['notification']['title'], flight)
    body = formatMsg(filters['notification']['body'], flight)
    image = getPic(flight["hex"])
    return [True, title, body, image]


def checkFilter(filter_config, value):
    if value is None:
        return True  # Missing value is ignored

    filter_type = filter_config.get("type", "AND")
    values = filter_config.get("values", [])

    if filter_type == "AND": return all(checkFilterVal(v, value) for v in values)
    elif filter_type == "OR": return any(checkFilterVal(v, value) for v in values)
    return True  # Unknown filter type, ignore


def checkFilterVal(v_config, value):
    op = v_config.get("type")
    v = v_config.get("value")
    try:
        if op == "EQUALS": return value.upper() == v.upper()
        elif op == "STARTS_WITH": return str(value.upper()).startswith(str(v.upper()))
        elif op == "ENDS_WITH": return str(value.upper()).endswith(str(v.upper()))
        elif op == "CONTAINS": return str(v) in str(value.upper())
        elif op == "LESS_THAN": return float(value) < float(v)
        elif op == "GREATER_THAN": return float(value) > float(v)
        elif op == "BETWEEN": return float(v[0]) <= float(value) <= float(v[1])
    except:
        return False  # Safely handle any type errors
    return False


def checkFilterPos(filter_config, lat, lon):
    if lat is None or lon is None:
        return True  # Skip if position missing

    filter_type = filter_config.get("type", "OR")
    values = filter_config.get("values", [])

    def inside_bounds(bounds):
        (lat_min, lon_min), (lat_max, lon_max) = bounds
        return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

    if filter_type == "AND":
        return all(inside_bounds(v["value"]) for v in values)
    elif filter_type == "OR":
        return any(inside_bounds(v["value"]) for v in values)
    return True  # Unknown filter type, ignore


def formatMsg(msg: str, flight: dict):
    return msg.replace("$hex;", str(flight.get("hex", )))\
              .replace("$flight;", str(flight.get("flight", "Unknown")))\
              .replace("$lat;", str(flight.get("lat", "Unknown")))\
              .replace("$lon;", str(flight.get("lon", "Unknown")))\
              .replace("$altitude;", str(flight.get("altitude", "Unknown")))\
              .replace("$track;", str(flight.get("track", "Unknown")))\
              .replace("$speed;", str(flight.get("speed", "Unknown")))\
              .replace("$hdg;", str(flight.get("track", "Unknown")))

def getPic(hex: str):
    url = f"https://api.planespotters.net/pub/photos/hex/{hex}"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return None
    data = response.json()
    photos = data.get("photos", [])
    if not photos:
        return None
    return photos[0]["thumbnail_large"]["src"]
from geopy.geocoders import Nominatim
import geopy.distance
import folium

Limit = 900

def find_distance(lat_1, lng_1, lat_2, lng_2):
    '''
    (float,float,float,float) -> float
    Return distance between two points 
    based on latitude and longtitude
    6300(radius) is used for calculations
    '''

    coords_1 = (lat_1, lng_1)
    coords_2 = (lat_2, lng_2)

    return geopy.distance.distance(coords_1, coords_2).km


def get_nearest_cities(places, top_10_nearest):
    """
    (list) -> list
    Return TOP-10 nearest places to the chosen one
    """

    global Limit
    for place in places:

        if Limit < 0:
            break
        try:
            locator = Nominatim(user_agent='Name')
            location = locator.geocode(place)
            lat, lng = location.latitude, location.longitude
            dist = find_distance(lat, lng, input_lat, input_lng)
            top_10_nearest.append([dist, lat, lng, place])
        except:
            continue


def read_csv(date):
    """
    (str) -> list
    Return list of locations from the file,
    where movies were filmed in the given year
    """

    with open("locations.csv", errors='ignore') as f:
        f.readline()
        locations = set()

        for line in f:
            line = line.strip().split(',')
            try:
                year = int(line[1])
            except:
                continue
            place = line[-1]

            if place not in locations:
                if year == int(date) and  place != "NO DATA":
                    locations.add(place)
    return list(locations)


def find_location(coordinates):
    """
    (str) -> tuple
    Return tuple of country, city and state found
    based on coordinates
    """

    locator = Nominatim(user_agent='Name')
    location = locator.reverse(coordinates, language='en')

    return (location.raw['address']['country'],\
            location.raw['address']['city'],\
            location.raw['address']['state'])


def check_the_nearest(list_of_places, user_place):
    """
    (list, tuple) -> set, set, set, set
    Checks if name of place, found using given coordinates,
    is in the name of location in the file
    """

    world = set()
    states = set()
    cities = set()
    countries = set()

    for country in list_of_places:
        if user_place[0] in country:
            countries.add(country)
        world.add(country)

    for city in list_of_places:
        if user_place[1] in  city:
            cities.add(city)

    for state in list_of_places:
        if user_place[2] in state:
            states.add(state)

    return states, cities, countries, world


def find_top_10(states, cities, countries, world):
    """
    Return list of the 10 nearest locations
    """

    top_10_nearest = []
    get_nearest_cities(cities, top_10_nearest)
    if len(top_10_nearest)>=10:
        return sorted(top_10_nearest)[:10]

    get_nearest_cities(states, top_10_nearest)
    if len(top_10_nearest)>=10:
        return sorted(top_10_nearest)[:10]

    get_nearest_cities(countries, top_10_nearest)
    if len(top_10_nearest)>=10:
        return sorted(top_10_nearest)[:10]

    get_nearest_cities(world, top_10_nearest)
    if len(top_10_nearest)>=10:
        return sorted(top_10_nearest)[:10]

    return sorted(top_10_nearest)[:10]


def get_EU_map():
    """
    Portrays the capitals of all EU members on the map
    """
    maps = folium.FeatureGroup(name="Countries")
    EU_countries = []

    with open('EU.txt') as f:
        EU_countries = f.readline().split(', ')
        EU_countries = [x.lower() for x in EU_countries]

    with open('countries.txt') as f:
        for country in f.readlines():
            country = country.split()
            if country[-1].lower() in EU_countries:
                maps.add_child(folium.Marker(location=[float(country[1]), float(country[2])],
                                       popup = country[-1],
                                       icon=folium.Icon(color='yellow')
                                       ))
    return maps


def print_map(top_10_nearest):
    '''
    (list) -> map
    Return map
    '''

    kart = folium.Map(location=[input_lat,input_lng])
    seam = folium.FeatureGroup(name="Films")

    for films in top_10_nearest:

        lt, ln = films[1], films[2]
        seam.add_child(folium.Marker(location=[lt, ln],
                                       popup = films[3]
                                       ))
    seam.add_child(folium.Marker(location=[input_lat, input_lng],
                                   icon=folium.Icon(color='orange')))
    European_union = get_EU_map()
    kart.add_child(seam)
    kart.add_child(European_union)
    kart.save('index.html')


if __name__ == '__main__':

    try:
        year = input("Please, enter a year you want to explore: ")
        input_lat, input_lng = [float(x) for x in input('Enter latitude and longitude: ').split()]
        print('Please wait 2-3 minutes')
        films = read_csv(year)
        coordinates_str =  find_location(str(input_lat) + ', ' + str(input_lng))
        states, cities, countries, world = check_the_nearest(films, coordinates_str)
        top_10_nearest = find_top_10(states, cities, countries, world)
        print('It will take a little time to run')
        print_map(top_10_nearest)
    except:
        print('Maybe your coordinates are improper')
        print('Try other coordinates')
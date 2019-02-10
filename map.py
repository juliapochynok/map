import folium
import copy 
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="specify_your_app_name_here")

from geopy.extra.rate_limiter import RateLimiter
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.1)


# GET YEAR

year1 = int(input("What year do you want to check: "))
while (year1 < 1901 or year1 > 2021):
    year1 = int(input("Please enter correct year( starting from 1900): "))
print("\n")

year2 = int(input("What other year do you want to check: "))
while (year2 < 1900 or year2 > 2021):
    year2 = int(input("Please enter correct year( starting from 1900): "))
print("\n")


# FUNCTIONS

def make_locations_dict(filename):
    '''
    (str) -> list
    Make a dict of locations of movies sets which was released in wanted year
    and amount of their appearance
    '''
    if type(filename) != str:
        return None
    locations_dict = {}
    locations_dict1 = {}
    with open(filename, encoding='utf-8', errors='ignore') as file:
        n = 0
        should_read =  False
        for line in file:
            n += 1
            if "==============" in line:
                should_read = True
            if (should_read):
                if len(line.strip().split()) > 3:
                    line_copy = copy.deepcopy(line)
                    line = line.strip()
                    line = line.split()
                    our_iterator = 0
                    amount = len(line)
                    for i in range(0, amount - 1):
                        if line[i][-1] == ')':
                            our_iterator = i
                            break
                    if line[our_iterator][0] == '(' and\
                    len(line[our_iterator]) == 6 :
                        line[our_iterator] = line[our_iterator].replace("(", "")
                        line[our_iterator] = line[our_iterator].replace(")", "")
                        if line[our_iterator].isdigit():
                            line[our_iterator] = int(line[our_iterator])
                            if line[our_iterator] == year1:
                                pointer = False
                                name = ""
                                for i in range(len(line_copy)-1, 0, -1):
                                    if line_copy[i] == '}':
                                        break
                                    if line_copy[i] == ',':
                                        pointer = True
                                    if pointer:
                                        a = line_copy[i]
                                        if line_copy[i] == ',':
                                            if name != "":
                                                name = name.strip()
                                                name = name.replace("," , "")
                                                if name not in locations_dict:
                                                    locations_dict[name] = 1
                                                else:
                                                    locations_dict[name] += 1
                                                name = ""
                                        name = line_copy[i] + name
                            elif line[our_iterator] == year2:
                                pointer1 = False
                                name1 = ""
                                for i in range(len(line_copy)-1, 0, -1):
                                    if line_copy[i] == '}':
                                        break
                                    if line_copy[i] == ',':
                                        pointer1 = True
                                    if pointer1:
                                        b = line_copy[i]
                                        if line_copy[i] == ',':
                                            if name1 != "":
                                                name1 = name1.strip()
                                                name1 = name1.replace("," , "")
                                                if name1 not in locations_dict1:
                                                    locations_dict1[name1] = 1
                                                else:
                                                    locations_dict1[name1] += 1
                                                name1 = ""
                                        name1 = line_copy[i] + name1
                            

    return locations_dict, locations_dict1




def popular_location(loc_dict):
    '''
    (dict) -> list
    Makes a list of 30 keys with the biggest values from dict
    '''
    top_locations = []
    for i in range(30):
        length = 0
        top_loc = ""
        for each in loc_dict:
            if loc_dict[each] > length:
                length = loc_dict[each]
                top_loc = each
        top_locations.append(top_loc)
        del loc_dict[top_loc]
    
    return top_locations



locations_list_year1, locations_list_year2 = make_locations_dict("locations.list")
popular_list1 = popular_location(locations_list_year1)
popular_list2 = popular_location(locations_list_year2)



# MAKING MAP

map = folium.Map(location=[16.7553023, -22.9462172], zoom_start=2.3)


try:
    fg_year1 = folium.FeatureGroup(name="Locations_Year1")


    for point in popular_list1:
        location = geolocator.geocode(point, timeout = 100)
        if location != None:
            lat = location.latitude
            lon = location.longitude
            fg_year1.add_child(folium.CircleMarker(location=[lat, lon],
                            radius= 2,
                            popup= "year " +str(year1)+"\n" + str(point),
                            fill_color='red',
                            color='red',
                            fill_opacity=1))

            map.add_child(fg_year1)

    fg_year2 = folium.FeatureGroup(name="Locations_Year2")


    for pointer in popular_list2:
        location1 = geolocator.geocode(pointer, timeout = 100)
        if location1 != None:
            lat1 = location1.latitude
            lon1 = location1.longitude
            fg_year2.add_child(folium.CircleMarker(location=[lat1, lon1],
                            radius= 2,
                            popup= "year " + str(year2)+"\n" + str(pointer),
                            fill_color='green',
                            color='green',
                            fill_opacity=1))

            map.add_child(fg_year2)

except:
    print("Done! Some locations are skipped")


fg_population = folium.FeatureGroup(name="Population")
fg_population.add_child(folium.GeoJson(data=open('world.json', 'r',
                encoding='utf-8-sig').read(),
                style_function=lambda x: {'fillColor':'green'
    if x['properties']['POP2005'] < 10000000
    else 'orange' if 10000000 <= x['properties']['POP2005'] < 20000000
    else 'red'}))

map.add_child(fg_population)
map.add_child(folium.LayerControl())

map.save('Map.html')
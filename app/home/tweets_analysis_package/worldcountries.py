import pycountry

countries2alpha_dict = {}
alpha2countries_dict = {}
cities2alpha_dict = {}
alpha2cities_dict = {}

for country in list(pycountry.countries):
    country_alpha2 = country.alpha_2
    country_name = country.name
    countries2alpha_dict[country_alpha2] = country_alpha2
    countries2alpha_dict[country_name] = country_alpha2
    if country_alpha2 not in alpha2countries_dict:
        alpha2countries_dict[country_alpha2] = []
        alpha2cities_dict[country_alpha2] = []
    alpha2countries_dict[country_alpha2].append(country_name)
    try:
        country_official_name = country.official_name
        countries2alpha_dict[country_official_name] = country_alpha2
        alpha2countries_dict[country_alpha2].append(country_official_name)
    except:
        pass

    for subdivision in list(pycountry.subdivisions.get(country_code=country_alpha2)):
        cities2alpha_dict[subdivision.name] = country_alpha2
        alpha2cities_dict[country_alpha2].append(subdivision.name)
import base64
import lxml.html
import pycountry
import re

from datetime import datetime
from logging import Logger

from stl.endpoint.base_endpoint import BaseEndpoint
from stl.geo.geocode import Geocoder

import json


class Pdp(BaseEndpoint):
    API_PATH = '/api/v3/StaysPdpSections' # hardcoded

    AMENITIES = {
        1:    'tv',
        4:    'wifi',
        5:    'a/c',
        8:    'kitchen',
        10:   'parking',
        11:   'smoking allowed',
        21:   'elevator',
        30:   'heating',
        33:   'washer',
        34:   'dryer',
        35:   'smoke alarm',
        36:   'carbon monoxide alarm',
        37:   'first aid kit',
        39:   'fire extinguisher',
        40:   'essentials',
        41:   'shampoo',
        44:   'hangers',
        45:   'hair dryer',
        46:   'iron',
        47:   'dedicated workspace',
        51:   'self check-in',
        52:   'smart lock',
        54:   'lockbox',
        57:   'private entrance',
        77:   'hot water',
        85:   'bed linens',
        86:   'extra pillows and blankets',
        89:   'microwave',
        90:   'coffee maker',
        91:   'refrigerator',
        92:   'dishwasher',
        93:   'dishes and silverware',
        94:   'cooking basics',
        95:   'oven',
        96:   'stove',
        99:   'bbq grill',
        100:  'private patio or balcony',
        101:  'private backyard',
        104:  'long term stays allowed',
        137:  'hot water kettle',
        139:  'ceiling fan',
        236:  'dining table',
        280:  'outdoor furniture',
        308:  'freezer',
        322:  'blender',
        611:  'shower gel',
        625:  'baking sheet',
        626:  'barbecue utensils',
        657:  'conditioner',
        665:  'cleaning products',
        667:  'drying rack',
        671:  'clothing storage',
        672:  'wine glasses',
        9999: 'security cameras'
    }

    SECTION_NAMES = ['amenities', 'description',
                     'host_profile', 'location', 'policies']

    def __init__(self, api_key: str, currency: str, logger: Logger):
        super().__init__(api_key, currency, logger)
        self.__geocoder = Geocoder()
        self.__regex_amenity_id = re.compile(r'^([a-z0-9]+_)+([0-9]+)_')

    @staticmethod
    def get_product_id(listing_id: str) -> str:
        return base64.b64encode(bytes(f'StayListing:{listing_id}', 'utf-8')).decode('utf-8')

    def get_listing(self, listing_id: str, data_cache: dict, geography: dict, reviews: list) -> dict:
        product_id = self.get_product_id(listing_id)
        response = self.get_raw_listing(listing_id)
        return self.__parse_listing_contents(response, data_cache[listing_id], geography, reviews) | {
            'product_id': product_id,
            'source':     self.SOURCE,
            'updated_at': datetime.utcnow(),
        }

    def get_raw_listing(self, listing_id: str) -> dict:
        url = self.__get_url(listing_id)
        return self._api_request(url)

    def collect_listings_from_sections(self, data: dict, geography: dict, data_cache: dict):
        """Get listings from "sections" (i.e. search results page sections)."""
        sections = data['data']['dora']['exploreV3']['sections']
        listing_ids = []
        for section in [s for s in sections if s['sectionComponentType'] == 'listings_ListingsGrid_Explore']:
            for listing_item in section.get('items'):
                listing_id = listing_item['listing']['id']
                self.__collect_listing_data(
                    listing_item, geography, data_cache)
                listing_ids.append(listing_id)

        return listing_ids

    def __collect_listing_data(self, listing_item: dict, geography: dict, data_cache: dict):
        """Collect listing data from search results, save in _data_cache. 

        The section data for each search result listing will later be combined with the PDP listing data in the 
        `parse_listing_contents()` method.
        """
        listing = listing_item['listing']
        pricing = listing_item['pricingQuote'] or {}
        city, neighborhood = self.__determine_city_and_neighborhood(
            listing, geography)

        data_cache[listing['id']] = {
            # get general data
            'avg_rating':             listing['avgRating'],
            'bathrooms':              listing['bathrooms'],
            'bedrooms':               listing['bedrooms'],
            'beds':                   listing['beds'],
            'business_travel_ready':  listing['isBusinessTravelReady'],
            'city':                   city,
            'host_id':                listing['user']['id'],
            'latitude':               listing['lat'],
            'longitude':              listing['lng'],
            'name':                   listing['name'],
            'neighborhood':           neighborhood,
            'neighborhood_overview':  listing['neighborhoodOverview'],
            'person_capacity':        listing['personCapacity'],
            'photo_count':            listing['pictureCount'],
            # 'photos':                 [p['picture'] for p in listing['contextualPictures']],
            'review_count':           listing['reviewsCount'],
            'room_and_property_type': listing['roomAndPropertyType'],
            'room_type':              listing['roomType'],
            'room_type_category':     listing['roomTypeCategory'],
            'star_rating':            listing['starRating'],
        }
        if pricing:
            # add pricing data
            data_cache[listing['id']] |= {
                # 'monthly_price_factor': pricing.get('monthlyPriceFactor'),
                # 'weekly_price_factor':  pricing.get('weeklyPriceFactor'),
                'price_rate':           self.__get_price_rate(pricing),
                'price_rate_type':      self.__get_rate_type(pricing),
                'total_price':          self.__get_total_price(pricing)
            }

    def __get_url(self, listing_id: str):
        query = {
            'operationName': 'StaysPdpSections',
            'locale':        self._locale,
            'currency':      self._currency
        }

        data = {
            'variables': {
                # encode with base64
                'id': base64.b64encode(bytes(f'StayListing:{listing_id}', 'utf-8')).decode('utf-8'),
                'pdpSectionsRequest': {
                    'adults': '1',
                    'bypassTargetings': False,
                    'categoryTag': None,
                    'causeId': None,
                    'checkIn': None,
                    'checkOut': None,
                    'children': None,
                    'disasterId': None,
                    'discountedGuestFeeVersion': None,
                    'displayExtensions': None,
                    'federatedSearchId': None,
                    'forceBoostPriorityMessageType': None,
                    'infants': '0',
                    'interactionType': None,
                    'layouts': ['SIDEBAR', 'SINGLE_COLUMN'],
                    'p3ImpressionId': 'p3_1687613160_8Y78vLPLFqV9bvpt', # hardcoded
                    'pdpTypeOverride': None,
                    'pets': 0,
                    'photoId': None,
                    'preview': False,
                    'previousStateCheckIn': None,
                    'previousStateCheckOut': None,
                    'priceDropSource': None,
                    'privateBooking': False,
                    'promotionUuid': None,
                    'relaxedAmenityIds': None,
                    'searchId': None,
                    'sectionIds': None,
                    'selectedCancellationPolicyId': None,
                    'selectedRatePlanId': None,
                    'splitStays': None,
                    'staysBookingMigrationEnabled': False,
                    'translateUgc': None,
                    'useNewSectionWrapperApi': False
                }
            },

            'extensions': {
                'persistedQuery': {
                    'version':    1,
                    'sha256Hash': 'aafa351c1f4399aa85bf6bc1d10f21c23428aa33d9a09505f5ee4fb5564c7aa0' # hardcoded
                }
            }
        }

        self._put_json_param_strings(data)

        url = BaseEndpoint.build_airbnb_url(self.API_PATH, query)
        url += f"&variables={data['variables']}"
        url += f"&extensions={data['extensions']}"

        return url

    # parse methods

    # # parse pdp data
    def __parse_pdp_data(self, data: dict) -> dict:
        return data['data']['presentation']['stayProductDetailPage']['sections']

    # # parse pdp metadata
    def __parse_pdp_metadata(self, data: dict) -> dict:
        return self.__parse_pdp_data(data)['metadata']

    # # parse pdp logging data
    def __parse_pdp_logging_data(self, data: dict) -> dict:
        return self.__parse_pdp_metadata(data)['loggingContext']['eventDataLogging']

    # # parse pdp sections
    def __parse_pdp_subsections(self, data: dict) -> dict:
        return self.__parse_pdp_data(data)['sections']

    # # parse section data

    def __parse_section_data(self, data: dict) -> dict:
        # get data
        sections = self.__parse_pdp_subsections(data)

        # get section data
        section_data = {}

        for section_name in self.SECTION_NAMES:
            if detail_list := [
                s
                for s in sections
                if s['sectionId'] == f'{section_name.upper()}_DEFAULT'
            ]:
                section_data[section_name] = detail_list[0]['section']

        return section_data

    # # parse amenities
    def __parse_amenities(self, section_data: dict) -> dict:

        # if amenities section exists
        if section_data.get('amenities'):
            # Collect amenity group data
            amenities_groups = section_data['amenities']['seeAllAmenitiesGroups']
            amenities_access = [g['amenities']
                                for g in amenities_groups if g['title'] == 'Guest access']
            amenities_avail = [
                amenity for g in amenities_groups for amenity in g['amenities'] if amenity['available']]
        else:
            amenities_access = amenities_avail = []

        return amenities_access, amenities_avail

    # # parse house rules
    def __parse_house_rules(self, section_data: dict) -> dict:

        # Collect house rules
        house_rules = []
        listing_expectations = None

        if section_data.get('policies'):
            if section_data['policies'].get('listingExpectations'):
                listing_expectations = self.__render_titles(
                    section_data['policies']['listingExpectations'])
            if section_data['policies'].get('houseRules'):
                house_rules = [r['title']
                               for r in section_data['policies']['houseRules']]

        return house_rules, listing_expectations

    # # parse description
    def __parse_description(self, section_data: dict) -> dict:

        return (
            self.__html_to_text(
                section_data['description']['htmlDescription']['htmlText']
            )
            if section_data.get('description')
            and section_data['description'].get('htmlDescription')
            else ''
        )

    def __parse_listing_contents(self, data: dict, listing_data_cached: dict, geography: dict, reviews: dict) -> dict:
        """Obtain data from an individual listing page, combine with cached data, and return dict."""

        # parsed data

        # # section data -> amenities, house rules, description
        section_data = self.__parse_section_data(data)

        amenities_access, amenities_avail = self.__parse_amenities(
            section_data)

        house_rules, listing_expectations = self.__parse_house_rules(
            section_data)

        description = self.__parse_description(section_data)

        # # metadata -> bookingPrefetchData, listingId

        metadata = self.__parse_pdp_metadata(data)

        # # logging data -> ratings
        logging_data = self.__parse_pdp_logging_data(data)
        listing_id = logging_data['listingId']

        # # reviews
        # reviews = self.__get_reviews(listing_id)

        # Structure data
        item = {
            'id': listing_id,
            'access': self.__render_titles(amenities_access[0])
            if amenities_access
            else None,
            'additional_house_rules': section_data['policies'].get(
                'additionalHouseRules'
            ),
            'allows_events': 'No parties or events' in house_rules,
            'amenities': self.__render_titles(
                amenities_avail, sep=' - ', join=False
            ),
            'avg_rating': listing_data_cached['avg_rating'],
            'bathrooms': listing_data_cached['bathrooms'],
            'bedrooms': listing_data_cached['bedrooms'],
            'beds': listing_data_cached['beds'],
            'business_travel_ready': listing_data_cached['business_travel_ready'],
            'can_instant_book': metadata['bookingPrefetchData']['canInstantBook'],
            'city': listing_data_cached.get('city', geography['city']),
            'coordinates': {
                'lon': listing_data_cached['longitude'],
                'lat': listing_data_cached['latitude'],
            },
            'country': geography['country'],
            'description': description,
            'host_id': listing_data_cached['host_id'],
            'house_rules': house_rules,
            'is_hotel': metadata['bookingPrefetchData']['isHotelRatePlanEnabled'],
            'latitude': listing_data_cached['latitude'],
            'listing_expectations': listing_expectations,
            'longitude': listing_data_cached['longitude'],
            'monthly_price_factor': listing_data_cached.get(
                'monthly_price_factor'
            ),
            'name': listing_data_cached.get('name', listing_id),
            'neighborhood': listing_data_cached.get('neighborhood'),
            'neighborhood_overview': listing_data_cached.get(
                'neighborhood_overview'
            ),
            'person_capacity': listing_data_cached['person_capacity'],
            'photo_count': listing_data_cached['photo_count'],
            # 'photos': listing_data_cached['photos'],
            'place_id': geography['placeId'],
            'price_rate': listing_data_cached.get('price_rate'),
            'price_rate_type': listing_data_cached.get('price_rate_type'),
            'province': geography.get('province'),
            'rating_accuracy': logging_data['accuracyRating'],
            'rating_checkin': logging_data['checkinRating'],
            'rating_cleanliness': logging_data['cleanlinessRating'],
            'rating_communication': logging_data['communicationRating'],
            'rating_location': logging_data['locationRating'],
            'rating_value': logging_data['valueRating'],
            'review_count': listing_data_cached['review_count'],
            'reviews': reviews,
            'room_and_property_type': listing_data_cached[
                'room_and_property_type'
            ],
            'room_type': listing_data_cached['room_type'],
            'room_type_category': listing_data_cached['room_type_category'],
            'satisfaction_guest': logging_data['guestSatisfactionOverall'],
            'star_rating': listing_data_cached['star_rating'],
            'state': geography['state'],
            'total_price': listing_data_cached.get('total_price'),
            'url': f"https://www.airbnb.com/rooms/{listing_id}",
            'weekly_price_factor': listing_data_cached.get('weekly_price_factor'),
        }

        self.__get_detail_property(
            item, 'transit', 'Getting around', section_data['location'].get('seeAllLocationDetails'), 'content')

        if section_data.get('host_profile'):
            self.__get_detail_property(
                item, 'interaction', 'During your stay', section_data['host_profile'].get('hostInfos'), 'html')

        return item

    def __determine_city_and_neighborhood(self, listing: dict, geography: dict):
        """Determine city and neighborhood. 

        It is way more complicated to get the city name than you'd expect. Airbnb sometimes puts the 
        neighborhood/borough/district into the city field, or give results from different cities entirely. Therefore,
        we use reverse geocoding (and, of course, advanced AI) to determine what the actual city name is. As a bonus,
        we also try to get the neighborhood.
        """
        public_address_components = list(
            map(str.strip, filter(bool, listing['publicAddress'].split(','))))
        search_city = geography['city']

        city = Pdp.__capitalize_first(listing['city'])
        neighborhood = listing['neighborhood']

        localized_city = Pdp.__capitalize_first(listing['localizedCity'])
        localized_neighborhood = listing['localizedNeighborhood']

        if search_city == city:
            return city, localized_neighborhood or neighborhood
        elif search_city == localized_city:
            city = localized_city

        address_city, address_neighborhood, address_district = None, None, None
        unknown_components = []

        for component in filter(bool, public_address_components):
            if component == search_city:
                address_city = component
            elif component == localized_neighborhood:
                address_neighborhood = component
            else:
                try:
                    result = pycountry.countries.lookup(
                        component) or pycountry.subdivisions.lookup(component)
                    continue  # skip countries and state/province subdivisions
                except LookupError:
                    unknown_components.append(component)

        if address_city and localized_neighborhood:
            return address_city, localized_neighborhood

        n_unknown_componenets = len(unknown_components)
        if n_unknown_componenets == 0:
            return address_city, neighborhood
        elif n_unknown_componenets == 1:
            if address_neighborhood and address_city:
                address_district = unknown_components.pop()
            elif address_city:
                address_neighborhood = unknown_components.pop()

        reverse_geo_address = self.__geocoder.reverse(
            listing['lat'], listing['lng'])

        if reverse_geo_address and 'city' in reverse_geo_address:
            if reverse_geo_address['city'] in [search_city, city, localized_city] or self.__geocoder.is_city(reverse_geo_address['city'], reverse_geo_address['country']):
                return reverse_geo_address['city'], localized_neighborhood

        if self.__geocoder.is_city((city or localized_city), reverse_geo_address['country']):
            return city or localized_city, neighborhood

        return city, neighborhood

    def __get_amenity_ids(self, amenities: list):
        """Extract amenity id from `id` string field."""
        for amenity in amenities:
            match = self.__regex_amenity_id.match(amenity['id'])
            yield int(match.group(match.lastindex))

    def __get_detail_property(self, item: dict, prop: str, title: str, prop_list: list, key: str):
        """Search for matching title in property list for prop. If exists, add htmlText for key to item."""
        if title in [i['title'] for i in prop_list]:
            item[prop] = self.__html_to_text(
                [i[key]['htmlText'] for i in prop_list if i['title'] == title][0])
        else:
            item[prop] = None

    @staticmethod
    def __capitalize_first(name: str | None) -> str:
        return name[0].upper() + name[1:] if name else name

    @staticmethod
    def __get_price_key(pricing) -> str:
        """Get price key from pricing data.

        Args:
            pricing (dict): Pricing data.

        Returns:
            str: Price key.
        """
        return 'price' if 'price' in pricing['structuredStayDisplayPrice']['primaryLine'] else 'discountedPrice'

    @staticmethod
    def __parse_price_str_to_dict(price_string: str, currency: str) -> int:
        """Summary: Convert price string to dictionary.

        Args:
        - price_string: Price string to convert.
        - currency: Currency symbol to remove from price_string.
           - If no currency is given, use SEARCH_CURRENCY from .env.

        Returns:
        - dict: {'amount': int, 'currency': str}
        """

        # if no price_string, return SEARCH_CURRENCY from .env
        if not currency:
            import os

            # convert with the same function
            return Pdp.__parse_price_str_to_dict(
                price_string,
                str(os.getenv('SEARCH_CURRENCY'))
            )

        # invert above dict
        currency_symbols = {
            'EUR': '€',
            'USD': '$',
            'PLN': 'zł'
        }

        # replace '\xa0' with ' ' in price_string
        # price_string = price_string.replace('\xa0', ' ')
        # encode utf-8
        from unicodedata import normalize
        price_str = normalize('NFKD', price_string).encode(
            'utf-8', 'ignore').decode()

        print(f"Price string: {price_str}")

        # get currency symbol
        currency_symbol = currency_symbols[currency]

        # remove currency symbol from price_string
        # price_string = price_string.replace(currency_symbol, '')

        # amount = numbers before first space
        amount = int(price_str.split(' ')[0].replace(',', ''))
        print(f"Amount: {amount}")

        # return dict
        return {'amount': amount, 'currency': currency, 'symbol': currency_symbol}

    @staticmethod
    def __get_price_rate(pricing) -> int | None:
        """_summary_:
        - Get price rate from pricing data.

        Args:
            pricing (dict): Pricing data.

        Returns:
        - if pricing exists, return price rate.
        - else, return None.

        """
        if pricing:
            price_key = Pdp.__get_price_key(pricing)
            res = pricing['structuredStayDisplayPrice']['primaryLine'][price_key].replace(
                '\xa0', ' ')
            return int(''.join(filter(str.isdigit, res)))

        return None

    @staticmethod
    def __get_rate_type(pricing) -> str | None:
        if pricing:
            return pricing['structuredStayDisplayPrice']['primaryLine']['qualifier']

        return None

    @staticmethod
    def __get_total_price(pricing) -> int | None:
        if pricing['structuredStayDisplayPrice']['secondaryLine']:
            price = pricing['structuredStayDisplayPrice']['secondaryLine']['price']
        else:
            price_key = Pdp.__get_price_key(pricing)
            price = pricing['structuredStayDisplayPrice']['primaryLine'][price_key]

        amount_match = ''.join(filter(str.isdigit, price))

        if amount_match == '':
            # raise ValueError('No amount match found for price: %s' % price)
            return None
        else:
            return int(amount_match)

    @staticmethod
    def __html_to_text(html: str) -> str:
        """Get plaintext from HTML."""
        return lxml.html.document_fromstring(html).text_content()

    @staticmethod
    def __render_titles(title_list: list, sep: str = ': ', join: bool = True) -> str | list:
        """Render list of objects with titles and subtitles into string."""
        lines = []
        for t in title_list:
            line = '{}{}{}'.format(t['title'], sep, t['subtitle']) if t.get(
                'subtitle') else t.get('title')
            lines.append(line)

        return '\n'.join(lines) if join else lines

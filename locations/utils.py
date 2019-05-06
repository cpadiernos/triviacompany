ne_states = (
    'Connecticut',
    'Maine',
    'Massachusetts',
    'New Hampshire',
    'New Jersey',
    'New York',
    'Pennsylvania'
    'Rhode Island',
    'Vermont',
    )
    
mw_states = (
    'Illinois',
    'Indiana',
    'Iowa',
    'Kansas',
    'Michigan',
    'Minnesota',
    'Missouri',
    'Nebraska',
    'North Dakota',
    'Ohio',
    'South Dakota'
    'Wisconsin',
    )    

s_states = (
    'Alabama',
    'Arkansas',
    'Delaware',
    'District of Columbia',
    'Florida',
    'Georgia',
    'Kentucky',
    'Louisiana',
    'Maryland',
    'Mississippi',
    'North Carolina',
    'Oklahoma',
    'South Carolina',
    'Tennessee',
    'Texas'
    'Virginia',
    'West Virginia',
    )

w_states = (
    'Alaska',
    'Arizona',
    'California',
    'Colorado',
    'Hawaii',
    'Idaho',
    'Montana',
    'Nevada',
    'New Mexico',
    'Oregon',
    'Utah',
    'Washington'
    'Wyoming',
    )

regions = {
    'NE': ne_states,
    'MW': mw_states,
    'S': s_states,
    'W': w_states}

def find_region(value, dict=regions):
    return next((k for k, v in dict.items() if value in v), None)
    
def google_map_address(self):
   base = 'https://www.google.ca/maps/place/'
   address = self.address.replace(" ", "+")
   city = self.city.name
   state = self.state.name
   zip = self.zip.code
   return (base + address + ",+" + city + ",+" + state + ",+" + zip)
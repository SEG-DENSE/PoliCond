# from poligraph terminology to my terminology
poli2my_dict = {}

poli2my_dict['cookie / pixel tag'] = 'cookie'
poli2my_dict['email address'] = 'email'
poli2my_dict['geolocation'] = 'location'
poli2my_dict['advertising id'] = 'advertising_id'
poli2my_dict['screen user name'] = 'username'
poli2my_dict['ip address'] = 'ip_address'
poli2my_dict['datum collect'] = 'datum'
poli2my_dict['information log from hardware'] = 'log'
poli2my_dict['datum for purpose'] = 'datum'
poli2my_dict['services service id'] = 'service_id'
poli2my_dict['postal address'] = 'address'
poli2my_dict['browser type'] = 'browser'
poli2my_dict['location data'] = 'location'

def translate_word_poli2my(input: str):
    if input in poli2my_dict:
        return poli2my_dict[input]
    return input


my2poli_dict = {}
my2poli_dict['cookie'] = 'cookie / pixel tag'
my2poli_dict['email'] = 'email address'
my2poli_dict['location'] = 'geolocation'


def translate_word_my2polo(input: str):
    if input in my2poli_dict:
        return my2poli_dict[input]
    return input

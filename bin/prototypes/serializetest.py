__author__ = 'dhkarimi'

import cPickle
from datetime import datetime
from pprint import pprint
import json

testdict = {
    'd': datetime.now(),
    'f': 1.2,
    'i': 1,
    's': "ads"}


def test_pickle():
    global testdict

    pstring = cPickle.dumps(testdict)

    pdict = cPickle.loads(pstring)

    print("Pickle String:")
    pprint(pstring)
    print("Orig dict")
    pprint(testdict)
    print("Loaded dict")
    pprint(pdict)


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


TIME_FORMAT_STR = "%a %b %d %H:%M:%S %Y"


def string_to_date(s):
    return datetime.strptime(s, TIME_FORMAT_STR)



def is_date(s):
    if s is None:
        return False
    try:
        string_to_date(s)
        return True
    except:
        return False



class MyDecoder(json.JSONDecoder):
    def default(self, s):
        print 'DECODING:', str(type(s)), str(s)
        defaultobj = json.JSONDecoder.decode(self,s)
        print 'DEFAUKT DECODING:', str(type(s)), str(s)

        return defaultobj




def test_json():
    global testdict

    pstring = json.dumps(testdict, cls=MyEncoder)

    pdict = json.loads(pstring, cls=MyDecoder)

    print("json String:")
    pprint(pstring)
    print("Orig dict")
    pprint(testdict)
    print("json dict")
    pprint(pdict)


if __name__ == "__main__":
    test_json()
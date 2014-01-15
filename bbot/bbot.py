#!/usr/bin/env python

import re
import pprint


def count_page(server, token, factor, searchResult):

    page = server.getPage(token,searchResult['id'])
    contents = page['content']
    print page
    markuplen = len(contents)

    print searchResult['title'], '\nmarkup len:', markuplen, '\npages:', \
        str(round(float(markuplen) / float(factor),1))

if options.search != None:
    results = server.search(token,options.search,1000)
    for r in results:
        print r
        msg = '\nIs this the wiki page you are looking for?'
        found = True if raw_input("%s (y/N) " % msg).lower() == 'y' else False
        if found:
            count_page(server, token, options.count_factor, r)
            exit(0)

        print '\n------------------------------------------------\n'




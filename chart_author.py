#!/usr/bin/env python

import sys
from invenio.bibauthorid_api import get_realauthor_data
# from invenio.bibauthorid_api import find_realauthor_ids

def do_stuff(author):

   time = 0

   papers = get_realauthor_data(author, 'bibrec_id')
   
   for i in range(0, len(papers)):
      print papers[i][1]

   #pull all cited papers of author's papers
   #find dates of all cites
   #calculate each point as time increases
   #(make sure to start time at date of first paper published!)
   #print out points

def main(authors):

   for author in authors:
      do_stuff(author)

if __name__ == "__main__":
   main(sys.argv[1:])


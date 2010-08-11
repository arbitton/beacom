#!/usr/bin/env python

import sys
from invenio.bibauthorid_api import get_realauthor_data
# from invenio.bibauthorid_api import find_realauthor_ids
from invenio.bibrank_citation_searcher import get_cited_by
# from invenio.bibrank_citation_searcher import get_cited_by_count
from invenio.search_engine import get_fieldvalues
import re

year_re = re.compile("^[0-9]{4}")

def find_cites(author):

   time = 0

   papers = get_realauthor_data(author, 'bibrec_id')
   
   year_dict = {}

   for i in range(0, len(papers)):
      cites = get_cited_by(int(papers[i][1]))
      # print papers[i][1], cites 
      for cite in cites:
         year = year_re.search(get_fieldvalues(cite, '269__C')[0])
         if int(year.group()) not in year_dict:
            year_dict[int(year.group())] = 1
         else:
            year_dict[int(year.group())] += 1
         # print year.group()

   print year_dict

   #pull all cited papers of author's papers
   #find years of all cites
   #calculate each point as time increases
   #(make sure to start time at date of first paper published!)
   #print out points

   return year_dict

def plot_points(year_dict, start_year):

   start = True

   for year in year_dict:
      # this is wrong, fix this
      if start:
         start_year = year
         start = False

      #calculate some stuff plx 

def main(authors):

   for author in authors:
      year_dict = find_cites(author)
      plot_points(year_dict)

if __name__ == "__main__":
   main(sys.argv[1:])


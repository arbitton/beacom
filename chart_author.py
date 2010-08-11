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

   print "# Author:", author
   papers = get_realauthor_data(author, 'bibrec_id')
   
   start_year = 0
   year_dict = {}
   total_cite_count = 0

   for i in range(0, len(papers)):
      cites = get_cited_by(int(papers[i][1]))
      # print papers[i][1], cites 
      for cite in cites:
         fieldvalues_yearlist = get_fieldvalues(cite, '269__C')
         if len(fieldvalues_yearlist) > 0:
            year = year_re.search(fieldvalues_yearlist[0])
            if year:
               if int(year.group()) not in year_dict:
                  year_dict[int(year.group())] = 1
               else:
                  year_dict[int(year.group())] += 1
               # print year.group()

   if len(year_dict) > 0:

      start_year = min(year_dict.keys())
      end_year = max(year_dict.keys())

      for i in range(start_year, end_year + 1):
         if i not in year_dict:
            year_dict[i] = 0
         total_cite_count += year_dict[i]
   else:
      print "# Author has no citations"

   # print year_dict

   #pull all cited papers of author's papers
   #find years of all cites
   #calculate each point as time increases
   #(make sure to start time at date of first paper published!)
   #print out points

   return year_dict, start_year, float(total_cite_count)

def plot_points(year_dict, start_year, total_cite_count):

   current_year = start_year
   start = True
   total_cites = 0 
   print "0 0"

   for year in year_dict:
      total_cites += year_dict[current_year]
      # print (cites in last five years), (total cites)
      print find_citeslast5years(year_dict, start_year, current_year)/total_cite_count, total_cites/total_cite_count
      current_year += 1

def find_citeslast5years(year_dict, start_year, current_year):

   result = 0

   if current_year - start_year >= 4:
      for i in range(0, 5):
         result += year_dict[current_year - i]
   else:
      while start_year <= current_year:
         result += year_dict[start_year]
         start_year += 1

   return result

def main(authors):

   for author in authors:
      year_dict, start_year, total_cite_count = find_cites(author)
      plot_points(year_dict, start_year, total_cite_count)

if __name__ == "__main__":
   main(sys.argv[1:])


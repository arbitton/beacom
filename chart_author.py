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
   
   year_dict = {}
   lifetime_cites = 0

   for paper in papers:
      cites = get_cited_by(int(paper[1]))
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
         lifetime_cites += year_dict[i]
   else:
      print "# Author has no citations"

   # print year_dict

   return year_dict, start_year, float(lifetime_cites)

def find_citesb(author):

   print "# Author:", author
   papers = get_realauthor_data(author, 'bibrec_id')
  
   year_dict = {}
   # print papers, "Papers"
   # print 'Number of papers:', len(papers)

   lifetime_cites = 0
   end_year = 0

   for paper in papers:
      paper_yearlist = get_fieldvalues(int(paper[1]), '269__C')
      # print paper_yearlist, "Paper year list"
      # print paper[1]
      if len(paper_yearlist) > 0:
         paper_year_match = year_re.search(paper_yearlist[0])
         if paper_year_match:
            paper_year = int(paper_year_match.group())
            # print paper_year
            cites = get_cited_by(int(paper[1]))
            # print cites
            for cite in cites:
               fieldvalues_yearlist = get_fieldvalues(cite, '269__C')
               if len(fieldvalues_yearlist) > 0:
                  cite_year_match = year_re.search(fieldvalues_yearlist[0])
                  if cite_year_match:
                     cite_year = int(cite_year_match.group())
                     if cite_year > end_year:
                        end_year = cite_year
                     # print "Years:", paper_year, cite_year
                     if paper_year not in year_dict:
                        year_dict[paper_year] = {cite_year: 1}
                     elif cite_year not in year_dict[paper_year]:
                        year_dict[paper_year][cite_year] = 1
                     else:
                        year_dict[paper_year][cite_year] += 1

   if len(year_dict) > 0:

      start_year = min(year_dict.keys())
      for i in year_dict:
         for j in year_dict[i]:
            lifetime_cites += year_dict[i][j]
   else:
      print "# Author has no citations"

   # print year_dict

   return year_dict, start_year, end_year, float(lifetime_cites)

def plot_points(year_dict, start_year, lifetime_cites):

   current_year = start_year
   total_cites = 0 
   print "0 0"

   for year in year_dict:
      total_cites += year_dict[current_year]
      # print (cites in last five years), (total cites)
      print find_citeslast5years(year_dict, start_year, current_year), total_cites, current_year
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

def plot_pointsb(year_dict, start_year, end_year, lifetime_cites):

   current_year = start_year
   print "0 0"

   total_cites = 0

   for year in range(start_year, end_year+1):
      for x in year_dict:
         if current_year in year_dict[x]:
            total_cites += year_dict[x][current_year]
      print find_citeslast5yearsb(year_dict, current_year), total_cites, current_year
      current_year += 1
       
def find_citeslast5yearsb(year_dict, current_year):

   result = 0

   for i in range(0, 5):
      if current_year - i in year_dict:
         for year in year_dict[current_year - i]:
            if year == current_year or year == current_year - 1 \
            or year == current_year - 2 or year == current_year - 3 \
            or year == current_year - 4:
               result += year_dict[current_year - i][year] 


   return result

def main(args):

   if args[0] == 'allpapers':
      year_dict, start_year, lifetime_cites = find_cites(args[1])
      plot_points(year_dict, start_year, lifetime_cites)
   else:
      year_dict, start_year, end_year, lifetime_cites = find_citesb(args[0])
      plot_pointsb(year_dict, start_year, end_year, lifetime_cites)

if __name__ == "__main__":
   main(sys.argv[1:])


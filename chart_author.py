#!/usr/bin/env python

import sys
from invenio.bibauthorid_api import get_realauthor_data
# from invenio.bibauthorid_api import find_realauthor_ids
from invenio.bibrank_citation_searcher import get_cited_by
# from invenio.bibrank_citation_searcher import get_cited_by_count
from invenio.search_engine import get_fieldvalues
import re

year_re = re.compile("^[0-9]{4}")

"""
This program is designed to be run at the command line.

The program takes an author id and outputs a list of x and y coordinates.
These coordinate pairs correspond to the author's accumulated citations
in the past five years versus the author's overall citation count. Each
point is calculated for each year in the author's career.

The first parameter it takes determines what type of plot should be generated:
   *"5years" denotes that only citations from papers written within the past 5 years
     be plotted when calculating the citations in the past 5 years
   *"allpapers" denotes that the program should create no constraint for calculating
     citations in the past 5 years based on when papers were published

The second parameter it takes determines how to scale the points:
   *"noscale" denotes that all points, with respect to both x and y coordinates
     should not be scaled
   *"lifetime" denotes that all points, with respect to both x and y coordinates
     should be divided by the author's lifetime cites

The final parameter it takes is the author's id number.

Examples:
python chart_author.py 5years noscale 65369
python chart_author.py allpapers lifetime 21315
python chart_author.py --help
etc.

"""


def find_cites(author):
   """
   Find and return all necessary components for plotting the data set.

   Returned values:
   1. year_dict: a dictionary keyed by years with values of the citations that occured in that year
   2. start_year: an integer that holds the year the first citation occured, used for calculating
      points to plot
   3. lifetime_cites: an integer holding the total amount of cites the author has in the present
      day, used to scale the final data set

   This definition first grabs a list of all the papers written by the author. From there,
   it iterates through the list, pulling the citations of each paper and incrementing the
   appropriate year in the year_dict dictionary for that citations year.

   Next, it iterates through the year ditionary to fill in values for missing years, setting them
   to zero. It also calculates the lifetime cites during this iteration.

   """

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

   """
   This defition plays the same role as the above defition of a similar name. However,
   it creates a different dictionary, as this definition is used only when the user
   wants to plot citations that occured in the past five years from papers published
   in the past five years only.

   The year dictionary in rather keyed by year of paper published. The values of the 
   keys are then another dictionary that holds years as the keys (of citations)
   with the values as the number of citations.
   Ex: {paper year: {citation year, count}}

   All other return values are the same, with the addition of 'end_year', which
   is an integer denoting the final year the author had a paper cited.

   """

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

def plot_points(year_dict, start_year, lifetime_cites, lifetime_scale):

   """
   This definition plots the points from the data set pulled in "find_cites"

   It scales the data based on the user inputted command.
   If the user opted for "lifetime", the program divides each point by the author's
   lifetime cites.

   """

   current_year = start_year
   total_cites = 0 
   print "0 0"

   if lifetime_scale:
      scale_factor = lifetime_cites
   else:
      scale_factor = 1

   for year in year_dict:
      total_cites += year_dict[current_year]
      # print (cites in last five years), (total cites)
      print find_citeslast5years(year_dict, start_year, current_year)/scale_factor, total_cites/scale_factor #, current_year
      current_year += 1

#############################
# All defitions that have a 'b' at the end represent the second implementation
# of this program, to plot cites only from papers within the past five years

def find_citeslast5years(year_dict, start_year, current_year):

   """
   This definition calculates and returns the number of cites that occured
   in the last five years given a specific year. This, paired with the overall_cites
   for that year constitute the x,y pair for a specific year.

   """

   result = 0

   if current_year - start_year >= 4:
      for i in range(0, 5):
         result += year_dict[current_year - i]
   else:
      while start_year <= current_year:
         result += year_dict[start_year]
         start_year += 1

   return result

def plot_pointsb(year_dict, start_year, end_year, lifetime_cites, lifetime_scale):


   """
   This defition plays the same role as the above defition of a similar name. However,
   it is used when the users opts to have the program plot cites from the past five
   years only from papers published within the past five years.

   """

   current_year = start_year
   print "0 0"

   total_cites = 0

   if lifetime_scale:
      scale_factor = lifetime_cites
   else:
      scale_factor = 1

   for year in range(start_year, end_year+1):
      for x in year_dict:
         if current_year in year_dict[x]:
            total_cites += year_dict[x][current_year]
      print find_citeslast5yearsb(year_dict, current_year)/scale_factor, total_cites/scale_factor #, current_year
      current_year += 1
       
def find_citeslast5yearsb(year_dict, current_year):

   """
   This defition plays the same role as the above defition of a similar name. However,
   it is used when the users opts to have the program plot cites from the past five
   years only from papers published within the past five years.

   """

   result = 0

   for i in range(0, 5):
      if current_year - i in year_dict:
         for year in year_dict[current_year - i]:
            if year == current_year or year == current_year - 1 \
            or year == current_year - 2 or year == current_year - 3 \
            or year == current_year - 4:
               result += year_dict[current_year - i][year] 


   return result

def helpmessage():
   print "This program is designed to be run at the command line.\n"
   print "The program takes an author id and outputs a list of x and y coordinates."
   print "These coordinate pairs correspond to the author's accumulated citations in the past"
   print "five years versus the author's overall citation count. Each point is calculated for"
   print "each year in the author's career.\n"
   print "The first parameter it takes determines what type of plot should be generated:"
   print "   *'5years' denotes that only citations from papers written within the past 5 years"
   print "    be plotted when calculating the citations in the past 5 years"
   print "   *'allpapers' denotes that the program should create no constraint for calculating"
   print "    citations in the past 5 years based on when papers were published\n"

   print "The second parameter it takes determines how to scale the points:"
   print "   *'noscale' denotes that all points, with respect to both x and y coordinates"
   print "     should not be scaled"
   print "   *'lifetime' denotes that all points, with respect to both x and y coordinates"
   print "     should be divided by the author's lifetime cites\n"
   
   print "The final parameter it takes is the author's id number.\n"

   print "Examples:"
   print "python chart_author.py 5years noscale 65369"
   print "python chart_author.py allpapers lifetime 21315"
   print "python chart_author.py --help"
   print "etc."

def main(args):

   if len(args) == 0:
      print "Incorrect input. For help page try: 'python chart_author.py --help'"
   elif args[0] == 'allpapers':
      if args[1] == 'lifetime':
         lifetime_scale = True
      elif args[1] == 'noscale':
         lifetime_scale = False
      else:
         print "Wrong second argument. Expecting 'lifetime' or 'noscale'."
         return None
      year_dict, start_year, lifetime_cites = find_cites(args[2])
      plot_points(year_dict, start_year, lifetime_cites, lifetime_scale)
   elif args[0] == '5years':
      if args[1] == 'lifetime':
         lifetime_scale = True
      elif args[1] == 'noscale':
         lifetime_scale = False
      else:
         print "Wrong second argument. Expecting 'lifetime' or 'noscale'."
         return None
      year_dict, start_year, end_year, lifetime_cites = find_citesb(args[2])
      plot_pointsb(year_dict, start_year, end_year, lifetime_cites, lifetime_scale)
   elif args[0] == '--help':
      helpmessage()
   else:
      print "Incorrect input. For help page try: 'python chart_author.py --help'"

if __name__ == "__main__":
   main(sys.argv[1:])


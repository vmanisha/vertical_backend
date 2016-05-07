import argparse
import pandas as pd
import numpy as np


# Construct several tables. 
#               Find the distribution of following variables:
#
#   a. task : users. Compute the number of users who provided task feedback
#   b. task : user_impressions. Compute the number of users who executed a
#    task.
#-----------------------------------------------------------------------------
#   c. task : vertical_views. Compute the number of times each vertical 
#       was shown as top result. 
#   d. task : queries. Compute the number of queries fired for the task.
#   e. task : clicks. Compute the number of clicks for the task. 
#   f. task : time . Compute the time spent on doing each task.
#   g. task : click_ranks. Compute the number of times a document was clicked
#   on a rank (remember to take page_number into account). 
#   h. task : time_to_first_click. Compute the time to first click for each
#   task. Compute mean and standard deviation. 
#   j. task : first_click_position. Compute the list of ranks that were clicked
#   first for task. 
#   k. task : last_click_position. Compute the ranks that were clicked last for
#   each task. 
#-----------------------------------------------------------------------------
#   h. task : vertical_queries. Compute the number of queries fired for the
#   task per vertical.
#   i. task : verticals_clicked. Compute the number of results that were clicked 
#   per vertical.
#   j. task : vertical_time. Compute the time doing task when a vertical was
#   top result. 
#   k. task : vertical_click_ranks. Compute the ranks that were clicked for
#   task given that vertical result was shown on top. 
#   l. task : time_to_click_veritcal. Compute the time to first click for each
#   task. Compute mean and standard deviation. 
#   m. task : first_click_position_vertical. Compute the list of ranks that were clicked
#   first for task for each vertical.  
#   n. task : last_click_position. Compute the ranks that were clicked last for
#   each task given a vertical was shown on top. 
#------------------------------------------------------------------------------



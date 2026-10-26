#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
from ydata_profiling import ProfileReport
import pandas as pd

raw_csv = 'data/raw/final_matches.csv'
clean_csv = 'data/processed/clean_final_matches.csv'

raw_df = pd.read_csv(raw_csv, na_filter=True)
clean_df = pd.read_csv(clean_csv, na_filter=True)

raw_profile = ProfileReport(raw_df, title='Raw EPL Matches')
clean_profile = ProfileReport(clean_df, title='Clean EPL Matches')

raw_profile.to_file('data/raw/raw_matches_report.html')
clean_profile.to_file('data/processed/clean_matches_report.html')
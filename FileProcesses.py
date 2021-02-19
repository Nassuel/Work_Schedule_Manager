import re
import os
import math
import numpy as np
import pandas as pd
from typing import Any, List
from pandas.core.frame import DataFrame
from datetime import datetime, timedelta

class FileParser():

    def __init__(self, img_filename_path: str, verbose=False) -> None:
        self.verbose = verbose
        self.file = img_filename_path
        self.file_name = self.file.split('\\')[-1].split('.')[0]
        self.df_file_location = './Schedule_Dfs/'+self.file_name+'.csv'
        self.rx_dict = {
            'date': re.compile(r'^([1-9]|1[012])[- /.]([1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$'),
            'day': re.compile(r'Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday'),
            'time': re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9] PM$|^([0-1]?[0-9]|2[0-3]):[0-5][0-9] AM$'),
            'number': re.compile(r'(?<!&#|\d[:\/-])(\d+(?:\.\d+)?)(?!%|[:\/-]\d)')
        }

    def _parse_line(self, line) -> Any:
        for key, rx in self.rx_dict.items():
            match = rx.search(line)
            if match:
                return key, match
        return None, None

    def parse_file(self) -> None:
        lines_of_data = []
        txt_filename = os.path.join(".","Recognized_Texts","recognized_{0}.txt".format(self.file_name))
        with open(txt_filename, 'r') as file:
            file_lines = file.readlines()
            # print(file_lines)
            time_count = 0
            line_data = {}
            for line in file_lines:
                key, match = self._parse_line(line)
                if key == 'date':
                    # Actual date
                    line_data['date'] = match.group()

                if key == 'time':
                    if time_count == 0:
                        # Changed On date
                        line_data['end_time'] = match.group()
                    if time_count == 1:
                        # Actual date
                        line_data['start_time'] = match.group()
                    time_count += 1
                
                if key == 'day':
                    # Data for that day ended
                    line_data['day'] = match.group()
                
                if '|||' in line:
                    lines_of_data.append(line_data)
                    time_count = 0
                    line_data = {}
        
        return lines_of_data

    def _output_df(self) -> None:
        """
        docstring
        """
        self.df.to_csv(self.df_file_location,index=False, header=True)
        return

    def parse_dataframe(self, lines_of_data) -> None:
        """
        docstring
        """
        self.df = pd.DataFrame(lines_of_data)
        new_columns = ['start_time_converted','end_time_converted']
        self.df[new_columns] = [np.NaN, np.NaN]

        new_columns_indexes = self._index_from_columndf(self.df, new_columns)

        for row in self.df.iterrows():
            actual_row = row[1]
            if self._nan_check(actual_row.start_time, actual_row.end_time, actual_row.date):
                start_date_str = str(actual_row.date) + ' ' + str(actual_row.start_time)
                end_date_str = str(actual_row.date) + ' ' + str(actual_row.end_time)

                start_datetime = datetime.strptime(start_date_str, "%m/%d/%Y %I:%M %p")
                end_datetime = datetime.strptime(end_date_str, "%m/%d/%Y %I:%M %p")

                # There are some stocker days where the departure is in the am
                if start_datetime > end_datetime:
                    end_datetime += timedelta(days=1)

                self.df.iloc[row[0], new_columns_indexes] = [start_datetime, end_datetime]
        
        # Since the substraction turns into timedelta, hours is not a timedelta properties, so have to get seconds and convert to hours
        self.df['duration'] = (self.df['end_time_converted'] - self.df['start_time_converted']).dt.seconds / 3600

        return

    @staticmethod
    def _index_from_columndf(df: DataFrame, str_column_array: List[str]) -> List[int]:
        """
        Used by parse_dataframe column for the iloc function dataframe as it takes the indexes of the columns we wanna parse
        """
        return [list(df).index(col) for col in list(df.columns) if col in str_column_array]

    @staticmethod
    def _nan_check(*value):
        """
        Check if value is nan
        """
        for val in value:
            try:
                if pd.isna(val) or math.isnan(val):
                    return False
            except TypeError:
                continue
        return True

def main():
    file_location = './Pictures/1-11-2021_1-17-2021_schedule.jpg'
    fl_prsr = FileParser(file_location)
    lines_of_data = []
    for i in range(1,8):
        lines_of_data.append(fl_prsr.parse_file(i))
    fl_prsr.parse_dataframe(lines_of_data)
    print(fl_prsr.df_file_location)
    fl_prsr._output_df()
        
if __name__ == '__main__':
    main()
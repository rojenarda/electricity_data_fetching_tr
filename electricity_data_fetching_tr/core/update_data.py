from .get_data import GetData
from .constants import DATASETS_DIRECTORY

import os
from datetime import datetime, timedelta

class UpdateData(GetData):
    def __init__(self, csv_name:str, dataset_classes:list=None, tz:str='Europe/Istanbul', dataset_dir=None):
        """
        Initialize the UpdateData class.
        
        Args:
            csv_path (str): Path of the CSV file to update.
            dataset_url (dict, optional): Contains URLs of the datasets and the keys to exctract.
            Defaults to DATASET_CLASSES.
            tz (str, optional): Timezone. Defaults to 'Europe/Istanbul'.
            dataset_dir (str, optional): Directory to save the datasets. Defaults to None.
        """
        
        
        super().__init__(dataset_classes, tz, dataset_dir)
        self.csv_path = f'{self.dataset_dir}/{csv_name}.csv'


    def _read_last_row(self):
        # Efficiently read the last row of the CSV file
        with open(self.csv_path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            end_byte = f.tell()
            while f.tell() > 0:
                f.seek(-2, os.SEEK_CUR)
                if f.read(1) == b'\n':
                    if f.tell() == end_byte - 1:
                        end_byte = f.tell() - 1
                        f.seek(-1, os.SEEK_CUR)
                        continue
                    else:
                        last_line = f.readline().decode()
                        return last_line.strip().split(',')
            f.seek(0)
            return f.readline().decode().strip().split(',')

    def _get_last_date(self):
        """
        Get the last date of the dataset.

        Returns:
            datetime: Last date of the dataset.
        """
        return self._parse_datetime(self._read_last_row()[0])
    
    def _today_date_str(self):
        """
        Get today's date.

        Returns:
            datetime: Today's date in ISO8601 format.
        """
        return self._convert_datetime_str(datetime.now(tz=self.tz))

    def _update_file_name(self, new_end_date:datetime):
        """
        Update the file name to include the new end date.

        Args:
            new_end_date (datetime): New end date.
        """
        file_name = self.csv_path.split('/')[-1]
        file_name = file_name.split('.')[0]
        file_name = file_name.split('_')
        file_name[-1] = new_end_date.strftime('%Y-%m-%d')
        file_name = '_'.join(file_name)
        try:
            os.rename(self.csv_path, f'{self.dataset_dir}/{file_name}.csv')
        except OSError as e:
            print(f"Error: {e.strerror}")
        self.csv_path = f'{self.dataset_dir}/{file_name}.csv'
    
    def get_data(self, replace_last_day:bool=False):
        """
        Update the dataset with the most recent data.
        Gets the data starting from the last date of the csv file to today's date.
        """
        
        if not replace_last_day:
            # Get the last date of the dataset and add one day to it to start from the next day.
            start_date = self._get_last_date() + timedelta(days=1)
        else:
            # Remove the last day's data and get the data starting from the last date of the dataset.
            temp_path = self.csv_path + '_temp'
            with open(self.csv_path, 'r') as file, open(temp_path, 'w') as temp_file:
                lines = file.readlines()
                # Write all but the last 24 lines to the temp file
                temp_file.writelines(lines[:-24])

            # Replace the original file with the updated temporary file
            os.remove(self.csv_path)
            os.rename(temp_path, self.csv_path)
            
            start_date = self._parse_datetime(lines[-1].split(',')[0])

            # Free the memory used
            del lines

        # Try to get tomorrow's values to be able to forecast tomorrow
        end_date = datetime.now() + timedelta(days=1)
        
        # Set hour values to 0
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        start_date_str = self._convert_datetime_str(start_date)
        end_date_str = self._convert_datetime_str(end_date)
        
        super().get_data(start_date_str, end_date_str, self.csv_path)
        
        # self._update_file_name(end_date)

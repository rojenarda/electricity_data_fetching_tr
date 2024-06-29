from electricity_data_fetching_tr import UpdateData

# Updates the given dataset with the most recent data.
# Fetches data starting from the last date of the dataset to today's date.
# Do not include the file extension in the filename (will automatically add .csv).
data = UpdateData('dataset_electricity_2017-01-01_2024-06-18')
data.get_data(replace_last_day=True)
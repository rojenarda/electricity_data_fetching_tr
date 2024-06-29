from electricity_data_fetching_tr import GetData
# Give start and end dates to create a new CSV with the data in that range.
data = GetData()
data.get_data('2017-01-01', '2024-06-18', file_name='data')

# Turkey Day Ahead Market Electricity Price Data Fetching

## Brief Description
This project fetches Turkey's day-ahead market electricity price data along with balancing market prices, forecasted demand, and supply data. The data is extracted from EPIAS' publicly available APIs and processed into a structured format for further analysis.

## Installation Instructions
To install the package, use the following command:
```bash
pip install electricity_data_fetching_tr
```

## Usage Examples
Below are examples of how to use the classes provided in this package to fetch and process the data.

To create a new dataset, use the code below. Give the desired date range. If you do not provide a file name, a file will be created with the name in the format: `dataset_electricity_<start_date>_<end_date>.csv`
```python
from electricity_data_fetching_tr import GetData
# Give start and end dates to create a new CSV with the data in that range.
data = GetData()
data.get_data('2017-01-01', '2024-06-18')
```

You can provide a file name, do not include the file extension.:
```python
data = GetData()
data.get_data('2017-01-01', '2024-06-18', 'data')
```
If you want the dataset to be saved someplace else that the current directory, you can provide the path:
```python
data = GetData(dataset_dir='path/to/dataset')
# The same can be used in UpdateData
data.get_data('2017-01-01', '2024-06-18', 'data')
```

Please note that the data before 2017 may contains duplicate timestamp indexes because of the summer-winter time transitions. 

Use the code below to update your existing dataset with recent information. This code fills the dataset with new data, starting from the last date in the dataset until the current day. If you pass the optional argument `replace_last_day` as `True`, the script will delete the last day's data from the dataset and re-fetch it. This is useful because Day-Ahead Market Prices are announced at 14.00 every day, and data can be fetched before that to perform forecasts. That in the next day, empty columns will be filled if you use this. 
```python
from electricity_data_fetching_tr import UpdateData

data = UpdateData('data')
data.get_data()
# Or, preferably:
data = UpdateData('data')
data.get_data(replace_last_day=True)
```

## License Information
This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for more details.

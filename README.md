# Geo_Data_Analysis

Use **main.py** for code execution. Must give the right required values as input at the begining lines of the script main.py. These input are ;

1- **input_data_directory**, the folder path where the raw files (.min) are placed.

2- **station_name**, the station from where the data was acquired.

3- **year**, the year of the data to be processed.

4- **margin_value**, the difference of data points that need to be stagged from the end of yesterday to the begining of present day.

5- **moving_avg_time**, the value of moving average. It should be in minutes.

6- **highlights**, the timestamps for the highlights in line plot. It should be in the form of a list and the no. of elements must be even where every two values represent start and end time of each highlight.

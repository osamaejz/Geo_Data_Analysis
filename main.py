from Geo_Data_Analysis.GDA import Geo_Data_Analytics

analysis = Geo_Data_Analytics()

input_data_directory = 'D:/NCAI-Neurocomputation Lab/Muneeza_Suparco/2009' ## Directory where the raw values are placed
station_name = 'Abg09' # station from where the data was acquired
year = str(2009) ## Year of the data to be processed
margin_value = 120 ## difference of data points that need to be stagged from the end of yesterday to the begining of today
moving_avg_time = 60 ## should be in minutes
highlights = [10.5, 13.5, 19.5, 21.5] ## for highlights in line plot. its input time stamps must be even in length. every two values represent start and end time of each highlight

mmdd_path = "D:/NCAI-Neurocomputation Lab/Muneeza_Suparco/mmdd2009.csv" ## list of quiet days

##converting .min files into xlsx
analysis.min_to_xlsx(input_data_directory, station_name, year) 

##transforming universal time into locl solar time
analysis.UT_to_LST(station_name, year, margin_value) 

## Segregating data of quiet days
analysis.QD_filtration(station_name, year, mmdd_path)

##performing computations for SqH calculation
analysis.process(station_name, year, moving_avg_time)

##visualizing outputs 
analysis.visualization(station_name, year, moving_avg_time, highlights)
from GDA import Geo_Data_Analytics

analysis = Geo_Data_Analytics()

input_data_directory = '2009' ## Directory where the raw values are placed
station_name = 'Abg09' # station from where the data was acquired
year = str(2010) ## Year of the data to be processed
margin_value = 120 ## difference of data points that need to be stagged from the end of yesterday to the begining of today
moving_avg_time = 60 # should be in minutes
highlight_begin = 10.5 # for highlights in line plot. 10.5 means 10:30 AM
highlight_end = 13.5 # for highlights in line plot. 13.5 means 13:30 PM
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
analysis.visualization(station_name, year, moving_avg_time, highlight_begin, highlight_end)
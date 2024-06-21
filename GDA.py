import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
import shutil
from scipy.interpolate import CubicSpline


class Geo_Data_Analytics:
    
    def __init__ (self):
        pass
    
    ## Function for .Min files conversion into .xlsx format    
    def min_to_xlsx (self, input_directory, station_name, year):
        
        min_files = [f for f in os.listdir(input_directory) if f.endswith('.min')]
        
        xls_save_path = f"Output/{station_name}/{year}/xls_raw_files"
        
        if not os.path.exists(xls_save_path):
            os.makedirs(xls_save_path)
        
        for filename in min_files:
            #pathstr, name, ext = os.path.splitext(filename)
            textFilename = os.path.join(input_directory, filename)
            fid = open(textFilename, 'r')
            data = pd.read_csv(fid, delim_whitespace=True, skiprows=26, header=None)
        
            save_file = filename[:-7] + ".xlsx"
            print("Writing file: " + save_file)
            out = os.path.join(xls_save_path, save_file)
            
            data.to_excel(out, index=False)


    ## Function to convert Universal Time into Local Solar Time
    def UT_to_LST (self, station_name, year, margin_value):
        
        # Input and Output Directories
        LST_save_path = f'Output/{station_name}/{year}/xls_LST_files' 
        xls_files_path = f'Output/{station_name}/{year}/xls_raw_files' 
        
        # Create output directory if it doesn't exist
        if not os.path.exists(LST_save_path):
            os.makedirs(LST_save_path)
        
        # List all files in the input directory
        xls_files = os.listdir(xls_files_path)
        
        # Loop through Files
        for i in range(len(xls_files) - 1):  # Adjusted the loop range so that loop value don't reach last file
        
            # Read data from two Excel files into matrices A and B
            data_1 = pd.read_excel(os.path.join(xls_files_path, xls_files[i]))
            data_2 = pd.read_excel(os.path.join(xls_files_path, xls_files[i+1]))
        
            # Concatenate data: the first part of the result (x) comes from the latter portion of A
            # and the second part comes from the initial portion of B
            merged_data = pd.concat([data_1.iloc[len(data_1) - margin_value:], data_2.iloc[:len(data_1) - margin_value]])
        
            print (f"Generating merged file for {xls_files[i]} and {xls_files[i+1]} ...")
            # Output File Writing
            save_file = f"{os.path.splitext(xls_files[i])[0]}_combined.xlsx"
            out = os.path.join(LST_save_path, save_file)
            merged_data.to_excel(out, index=False)


    ## Function to separate excel files of quiet days
            
    def extract_id_from_filename(self, filename):
        base_name = os.path.splitext(filename)[0]  # Remove file extension
        id_part = base_name[7:11]  # Get the last 4 characters
        if id_part[0] == '0':  # If the first character of the 4-character part is '0', it's a 3-digit ID
            return id_part[1:]  # Return the last 3 characters
        else:
            return id_part  # Return all 4 characters
        
    def QD_filtration(self, station_name, year, mmdd_path):
        
        data_files_dir = f'Output/{station_name}/{year}/xls_LST_files' 
        QD_save_dir = f'Output/{station_name}/{year}/QD_files'
        
        os.makedirs(QD_save_dir, exist_ok=True)
        
        mmdd = pd.read_csv(mmdd_path)
        
        Days_list = mmdd['Date'].tolist()
        
        Days_list_str = [str(id) for id in Days_list]
        
        for filename in os.listdir(data_files_dir):
            if filename.endswith('.xlsx'):  # Check if the file is an Excel file
                file_id = self.extract_id_from_filename(filename)
                if file_id in Days_list_str:
                    print(f"Copying excel file with the ID: {file_id} to QD folder")
                    source_path = os.path.join(data_files_dir, filename)
                    destination_path = os.path.join(QD_save_dir, filename)
                    shutil.copy2(source_path, destination_path)  # Copy the file to the QD folder
        
        print("All files have been copied successfully.")


    ## Function to process inputs and perform computations
    def process(self, station_name, year, moving_mins_time):
        
        #LST_files_path = f'Output/{station_name}/{year}/xls_LST_files' 
        QD_files_path = f'Output/{station_name}/{year}/QD_files'
        
        SqH_save_path = f'Output/{station_name}/{year}/SqH'
        
        prompt = f"SqH{moving_mins_time}_{station_name}.xlsx"
        
        output_file = os.path.join(SqH_save_path, prompt)
        
        if not os.path.exists(SqH_save_path):
            os.makedirs(SqH_save_path)
        
        data_files = [f for f in os.listdir(QD_files_path) if f.endswith('.xlsx')]
        
        print("Reading LST Data Files")
        data = [pd.read_excel(os.path.join(QD_files_path, file), header = 0) for file in data_files]
        
        Coldata = np.dstack([df.to_numpy() for df in data])
        
        Coldata[Coldata == 99999] = np.nan
        
        print("Computing He....")        
        He = np.zeros((Coldata.shape[0], Coldata.shape[2]))
        
        for i in range(Coldata.shape[2]):
            Sum = np.array(np.square(Coldata[:, 2, i]) + np.square(Coldata[:, 3, i])).astype(float)
            He[:, i] = np.sqrt(Sum)
            #He[:, i] = np.sqrt(np.nan_to_num((Coldata[:, 2, i] ** 2) + (Coldata[:, 3, i] ** 2)))
        
        # # HEM method 1
            
        # Hem = np.zeros((He.shape[0] // moving_mins_time, He.shape[1]))
        
        # for j in range(He.shape[0] // moving_mins_time):
        #     i = (j + 1) * moving_mins_time
        #     Hem[j, :] = np.nanmean(He[i - moving_mins_time:i, :], axis=0)
            
        # HEM method 2   
        print("Computing Hem....")       
        Hem = np.zeros((He.shape[0] // moving_mins_time, He.shape[1]))
        
        for j in range(1, len(He) // moving_mins_time + 1):
            start_index = (j - 1) * moving_mins_time
            end_index = min(j * moving_mins_time, He.shape[0])
            
            # Use a temporary variable for the moving mean calculation
            tmpHem = pd.DataFrame(He[start_index:end_index, :]).rolling(window=60, min_periods=1).mean()
            
            # Ensure that the dimensions are compatible and assign to Hem
            Hem[j - 1, :] = tmpHem.iloc[0, :]
        
        print("Computing Heavg....")       
        Heavg = np.zeros((1, Hem.shape[1]))
        
        for k in range(len(data_files)):
            Heavg[0, k] = np.nanmean(Hem[[0, 1, 21, 22], k])
        
        # Subtract Heavg from Hem
        delHe = Hem - Heavg
        
        print("Computing SqH....")   
        delHep = np.zeros((1, len(data_files)))
        SqH = np.zeros((24, len(data_files)))
        
        # Loop over each filename
        for i in range(len(data_files)):
            for k in range(24):
                delHep[0, i] = (delHe[0, i] - delHe[22, i]) / 23
                SqH[k, i] = delHe[k, i] + (k * delHep[0, i])
                
        df = pd.DataFrame(SqH)
        
        print("Writing SqH file: {output_file}")   
        df.to_excel(output_file)
        
        
    ## Function for outputs visualization   
    def visualization (self, station_name, year, moving_avg_time, highlights):
            
        #LST_files_path = f'Output/{station_name}/{year}/xls_LST_files' 
        QD_files_path = f'Output/{station_name}/{year}/QD_files'
        data_files = [f for f in os.listdir(QD_files_path) if f.endswith('.xlsx')]
        
        SqH_file_path = f'Output/{station_name}/{year}/SqH/SqH{moving_avg_time}_{station_name}.xlsx'
        SqH = np.array(pd.read_excel(SqH_file_path, index_col=0))
        
        output_dir = f'Output/{station_name}/{year}/plots'
        os.makedirs(output_dir, exist_ok=True)
        
        # Width and height in inches
        width = 8
        height = 6
        lw = 2  # Line width
        msz = 8  # Marker size  
        
        Hrs = np.arange(1, 25)  # Hours from 1 to 24
        
        out = [re.findall(r'\d+', filename) for filename in data_files]
        out = np.array([int(num) for sublist in out for num in sublist])
        
        # Loop over each filename
        for ii in range(len(data_files)):
            #plt.figure(figsize=(width, height))
            fig, ax = plt.subplots(figsize=(width, height))
            
            # Plotting the data
            #plt.plot(Hrs, SqH[:, ii], 'b-o', linewidth=4, markersize=4, label=f'Actual SqH: {moving_avg_time} mins mvg avg on LST')
        
            cs = CubicSpline(Hrs, SqH[:, ii])
            
            # Create a range of x values for plotting the spline
            x_new = np.linspace(min(Hrs), max(Hrs), 1000)
            y_new = cs(x_new)    
            
            ax.plot(x_new, y_new, 'b-o', linewidth=3, markersize=3, label=f'Actual SqH: {moving_avg_time} mins mvg avg on LST')
        
            plt.xlim([0, 25])
            plt.xticks(np.arange(0, 26, 2), fontsize=18)
            plt.ylim([-35, 65])
            plt.yticks(np.arange(-35, 66, 5), fontsize=18)
        
            plt.xlabel('Time [hr]', fontsize=18)
            plt.ylabel('Sq(H) [nT]', fontsize=18)
        
            plt.legend(loc='best', fontsize=14)
            
            # ax.axvspan(highlight_begin, highlight_end, color="blue", alpha=0.3)
            
            # if highlight_begin_2 is not None and highlight_end_2 is not None:
            
            #     ax.axvspan(highlight_begin_2, highlight_end_2, color="blue", alpha=0.3)
                
            a = 0   
            for j in range (int(len(highlights) / 2)):
                ax.axvspan(highlights[j+a], highlights[j+1+a], color= 'blue', alpha=0.3)    
                a += 1
            
            plt.grid(True, which='both')
            plt.title(f'{station_name} {out[ii]}', fontsize=20)
        
                   
            # Save the plot
            print(f"Saving figure {station_name} {out[ii]}")
            plt.savefig(os.path.join(output_dir, f'plot_{ii+1}.png'))
            plt.show()    
            plt.close()
        
        print("Plots saved successfully.")
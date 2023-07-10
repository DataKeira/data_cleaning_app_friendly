# Testing branch Render Live

Test and merge new updates while others can still use the orginial app on the main branch. 

## How to Use

1. **Enter Target Species**: Specify the target species for data filtering. Only rows with the specified species in the "Organism" column will be included in the analysis. For example (Homo sapiens OX=9606), include both the species and OX number. Is case sensitive. 

2. **Upload CSV File**: Drag and Drop, or select an exsisting file. A message will pop-up stating that your file has be uploaded successfully.

4. **Clean Data**: Click the "Clean Data" button to process the data based on the specified target species and column filtering. A message will pop-up stating that your cleaned data is ready for download.

5. **Download Clean Data**: Click the "Download Cleaned Data" button. A csv file called cleaned_data.csv will appear in your downloads. Name your file and save accordingly.

## Dependencies

- Python 3.6 or higher
- pandas 2.0.3
- dash 2.11.0
- dash-core-components
- dash-html-components
- Requirements txt file included

## How to Run on a local server

To run the ProteoCore Data Cleaning Dash App, follow these steps:

1. Clone or download this GitHub repository.

2. Install the required Python packages using pip:

```bash
pip install pandas dash dash-core-components dash-html-components gunicorn
```

3. Open the terminal or command prompt, navigate to the directory where the app code is located, and run the app:

4. Create a new python file (e.g.,'app.py') and copy the code downloaded from the repository into it.
   
5. Run the app:

```bash
python app.py
```

6. Open a web browser and go to the following address to access the Dash app:

```bash
http://127.0.0.1:8050/
```

7. The app can be stopped by going into the terminal or cammand prompt where the app is running and press 'Ctrl + C'.

## Note

- Make sure to have the CSV file containing the proteomics data in the correct format with required columns such as "Organism," "Gene," and "Intensity" columns.

- The app will fill empty values in the "Gene" column with the "Entry Name" value for identification.

- The app will remove rows where all columns except the "Gene" column have a value of 0.

- Columns containing ("MaxLFQ", "Unique", or "Total") Intensity in their names will be excluded from the analysis.

- Duplicates will be aggragated instead of dropped.

- If you wish to add labels to your sample columns you must do so manually onto the downloaded cleaned data csv file.

- Does not remove keratin contamination if your target species is Human.

## Feedback and Contributions

Your feedback and contributions to this project are highly appreciated! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on GitHub.


import pandas as pd
import io
import base64
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import csv
import os

#helper function to extract file extension from filename
def get_file_extension(filename):
    _, extension = os.path.splitext(filename)
    return extension.lower() if extension else None

app_render = dash.Dash(__name__, external_stylesheets=[
    'https://cdn.rawgit.com/chriddyp/0247653a7c52feb4c48437e1c1837f75/raw/a68333b876edaf62df2efa7bac0e9b3613258851/dash.css'
])
server = app_render.server
app_render.layout = html.Div([
    html.H1('ProteoCore Data Cleaning App', style={'text-align': 'center', 'font-family': 'Lato'}),
    html.H4('Upload a TSV or CSV file and clean your data!', style={'text-align': 'center'}),
    dcc.Upload(
        id='data-file-upload',
        children=html.Div(['Drag and Drop or ', html.A('Select File')]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'font-family': 'Lato',
        },
        multiple=False
    ),
    dcc.Store(id='upload-status'),  
    # Store component to track the file upload status
    html.Div(id='upload-message', style={'font-family': 'Lato'}),  
    # Display the message here
    html.Br(),
    html.Div([
    dcc.Input(
        id='target-species-input',
        type='text',
        placeholder='Enter Species (matches Organism column exactly)',
        style={
            'width': '50%',
            'padding': '10px',
            'font-family': 'Lato',
        }
    ),
    html.Button(
        'Clean Data',
        id='clean-button',
        n_clicks=0,
        style={
            'padding': '10px',
            'font-family': 'Lato',
            'margin': 'auto',
            'display': 'flex',  # Use flexbox to center the button text
            'justify-content': 'center',  # Horizontally center the button text
            'align-items': 'center',  # Vertically center the button text
        }
    ),
    html.A(
    html.Button(
        'Download Cleaned Data', 
        id='download-button', disabled=True,
        style={
            'padding': '10px',
            'font-family': 'Lato',
            'margin': 'auto',
            'display': 'flex',  # Use flexbox to center the button text
            'justify-content': 'center',  # Horizontally center the button text
            'align-items': 'center',  # Vertically center the button text
        },
    ),
        id='download-link',
        download="cleaned_data.csv",
    ),
    ],
    style={'display': 'flex', 'justify-Content': 'center', 'alignItems': 'center', 'textAlign': 'center'}),
    html.Br(),
    html.Div(id='cleaned-data-output', style={'font-family': 'Lato'}),
    
])


def clean_data(target_species, data_contents, file_extension):
    if data_contents is not None:
        # Read the data from the uploaded TSV or CSV file
        content_type, content_string = data_contents.split(',')
        decoded = base64.b64decode(content_string)
        
        #check and read file
        if file_extension.lower() == '.csv':
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif file_extension.lower() == '.tsv':
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t', quoting=csv.QUOTE_NONE)      
        else:
            return None

        # Filter the data to include only rows with the target species
        filtered_data_row = df[df['Organism'] == target_species]

        # Any empty values in the 'Gene' column will be filled with the 'Entry Name' of that row for identification
        filtered_data_row['Gene'] = filtered_data_row['Gene'].fillna(filtered_data_row['Entry Name'])

        # Setting a value to 'Gene' and 'Intensity' columns except 'MaxLFQ' or 'Unique intensity'
        columns_to_keep = ['Gene'] + [col for col in filtered_data_row.columns if 'Intensity' in col and 'MaxLFQ' not in col and 'Unique' not in col and 'Total' not in col]
        
              # Removes all columns except columns chosen above
        filtered_data_column = filtered_data_row[columns_to_keep]

        # Filter columns that contain the word 'Intensity'
        intensity_columns = filtered_data_column.columns[filtered_data_column.columns.str.contains('Intensity')]

        # Filter columns that contain the word 'Intensity'
        intensity_columns = [col for col in filtered_data_column.columns if 'Intensity' in col]

        # Create a DataFrame to store cleaned data with identifiers
        cleaned_data_with_identifiers = pd.DataFrame(columns=['Gene'] + intensity_columns)

        #initialize empty list to hold row with identifiers

        rows_with_identifiers = []

        # Add isoform identifiers to duplicates
        gene_counts = {}
        for index, row in filtered_data_column.iterrows():
            gene = row['Gene']
            if gene in gene_counts:
                gene_counts[gene] += 1
                gene_with_identifier = f"{gene}_{gene_counts[gene]}"
            else:
                gene_counts[gene] = 1
                gene_with_identifier = gene

             # Create a dictionary with the identifier and intensity values
            identifier_and_intensity = {'Gene': gene_with_identifier}
            for col in intensity_columns:
                identifier_and_intensity[col] = row[col]

            
            # append row with identifier and intensities
            rows_with_identifiers.append(identifier_and_intensity)

        # Append the row with the identifier and intensities to the DataFrame
        cleaned_data_with_identifiers = pd.DataFrame(rows_with_identifiers)

        # Convert the cleaned data to CSV format
        csv_string = cleaned_data_with_identifiers.to_csv(index=False, encoding='utf-8')


        return csv_string


        
    return None

@app_render.callback(
    [
        Output('upload-status', 'data'),  
        # Store the file upload status in the dcc.Store component
        Output('upload-message', 'children'),  # Display the message here
    ],
    Input('data-file-upload', 'contents'),
)

def update_upload_status(data_contents):
    if data_contents is not None:
        # File uploaded successfully, update the status to True and show the message
        return True, "File uploaded successfully"

    # No file uploaded yet, status is False and no message
    return False, ""

@app_render.callback(
     [
        Output('download-button', 'disabled'),
        Output('download-link', 'href'),
        Output('cleaned-data-output','children'),
    ],
    Input('clean-button', 'n_clicks'),
    State('target-species-input', 'value'),
    State('data-file-upload', 'contents'),
    State('data-file-upload', 'filename'),
    State('upload-status', 'data'),
)
def update_cleaned_data(n_clicks, target_species, data_contents, filename, uplaod_status):
    if n_clicks is None or n_clicks == 0:
        return True, None, ""
    
    if data_contents is not None:
        file_extension = get_file_extension(filename)
        cleaned_data_csv = clean_data(target_species, data_contents, file_extension)

        if cleaned_data_csv is not None:
            # If the cleaned_data_csv is not None, enable the button and provide the download link
            href = "data:text/csv;charset=utf-8," + cleaned_data_csv
            return False, href,"Data has been cleaned successfully!"
    
    return True, None,""

if __name__ == '__main__':
    app_render.run_server(debug=True)

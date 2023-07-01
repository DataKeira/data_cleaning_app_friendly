import pandas as pd
import io
import base64
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

app_render = dash.Dash(__name__, external_stylesheets=[
    'https://cdn.rawgit.com/chriddyp/0247653a7c52feb4c48437e1c1837f75/raw/a68333b876edaf62df2efa7bac0e9b3613258851/dash.css'
])

app_render.layout = html.Div([
    html.H1('ProteoCore Data Cleaning App', style={'text-align': 'center', 'font-family': 'Lato'}),
    html.H4('Upload a CSV file and clean your data!', style={'text-align': 'center'}),
    dcc.Upload(
        id='csv-file-upload',
        children=html.Div(['Drag and Drop or ', html.A('Select CSV File')]),
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
        placeholder='Enter Target Species (e.g., Homo sapiens OX=9606)',
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

def clean_data(target_species, csv_contents,):
    if csv_contents is not None:
        # Read the data from the uploaded CSV file
        content_type, content_string = csv_contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
      
        # Filter the data to include only rows with the target species
        filtered_data_row = df[df['Organism'] == target_species]

        # Any empty values in the 'Gene' column will be filled with the 'Entry Name' of that row for identification
        filtered_data_row['Gene'] = filtered_data_row['Gene'].fillna(filtered_data_row['Entry Name'])

        # Setting a value to 'Gene' and 'Intensity' columns except 'MaxLFQ' or 'Unique intensity'
        columns_to_keep = ['Gene'] + [col for col in filtered_data_row.columns if 'Intensity' in col and 'MaxLFQ' not in col and 'Unique' not in col]
        
              # Removes all columns except columns chosen above
        filtered_data_column = filtered_data_row[columns_to_keep]

        # Filter columns that contain the word 'Intensity'
        intensity_columns = filtered_data_column.columns[filtered_data_column.columns.str.contains('Intensity')]

        # Combine the duplicate rows based on the 'Gene' column and sum the values in the intensity columns
        cleaned_data = filtered_data_column.groupby('Gene')[intensity_columns].sum().reset_index()
        
        # Check if all columns except 'Gene' have a value of 0
        mask = (cleaned_data.loc[:, cleaned_data.columns != 'Gene'] == 0).all(axis=1)

        # Filter the DataFrame to remove rows where the condition is True
        clean_data = cleaned_data[~mask]

        # Convert the cleaned data to CSV format
        csv_string = clean_data.to_csv(index=False, encoding='utf-8')

        return csv_string
        
    return None

@app_render.callback(
    [
        Output('upload-status', 'data'),  
        # Store the file upload status in the dcc.Store component
        Output('upload-message', 'children'),  # Display the message here
    ],
    Input('csv-file-upload', 'contents'),
)

def update_upload_status(csv_contents):
    if csv_contents is not None:
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
    State('csv-file-upload', 'contents'),
    State('upload-status', 'data'),
)
def update_cleaned_data(n_clicks, target_species, csv_contents, uplaod_status):
    if n_clicks is None or n_clicks == 0:
        return True, None, ""

    cleaned_data_csv = clean_data(target_species, csv_contents)
    

    if cleaned_data_csv is not None:
        # If the cleaned_data_csv is not None, enable the button and provide the download link
        href = "data:text/csv;charset=utf-8," + cleaned_data_csv
        return False, href,"Data has been cleaned successfully!"
    
    return True, None,""

if __name__ == '__main__':
    app_render.run_server(debug=True)


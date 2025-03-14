# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load the SpaceX launch data from a CSV file into a pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get the maximum and minimum values for Payload Mass (kg)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize the Dash application
app = dash.Dash(__name__)

# Define the layout of the application
app.layout = html.Div([
    # Title of the dashboard
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),
    
    # Dropdown for selecting the launch site
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'All Sites'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        placeholder='Select a Launch Site Here',
        value='All Sites',  # Default selection is 'All Sites'
        searchable=True     # Allow search functionality in the dropdown
    ),
    html.Br(),  # Line break
    
    # Graph for the success rate pie chart
    dcc.Graph(id='success-pie-chart'),
    html.Br(),
    
    # Text to display before the payload range slider
    html.P("Payload range (Kg):"),
    
    # Range slider for selecting the payload mass range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,        # Minimum payload mass (kg)
        max=10000,    # Maximum payload mass (kg)
        step=1000,    # Step size for the slider
        marks={i: str(i) for i in range(0, 10001, 1000)},  # Slider marks at intervals of 1000
        value=[min_payload, max_payload]  # Default value is the full payload range
    ),
    
    # Graph for the scatter chart showing the correlation between payload and success
    dcc.Graph(id='success-payload-scatter-chart')
])

# Callback to update the pie chart based on the selected launch site
@app.callback(
    Output('success-pie-chart', 'figure'),  # Output to the pie chart
    Input('site-dropdown', 'value')         # Input from the dropdown (selected launch site)
)
def update_pie_chart(selected_site):
    # If 'All Sites' is selected, show the success rate for all sites combined
    if selected_site == 'All Sites':
        fig = px.pie(
            spacex_df.groupby('Launch Site')['class'].mean(),  # Calculate average success rate by site
            names=spacex_df.groupby('Launch Site')['Launch Site'].first(),  # Use site names
            title='Total Success Launches by Site'  # Title of the chart
        )
    else:
        # If a specific site is selected, filter data by that site and show success rate
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            site_data['class'].value_counts(normalize=True),  # Calculate the normalized success count
            names=site_data['class'].unique(),  # Use unique success/fail labels
            title=f'Total Success Launches for Site {selected_site}'  # Title with the selected site
        )
    return fig  # Return the figure to update the chart

# Callback to update the scatter chart based on selected site and payload range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),  # Output to the scatter chart
    [
        Input('site-dropdown', 'value'),  # Input from the dropdown (selected launch site)
        Input('payload-slider', 'value')  # Input from the payload slider (selected payload range)
    ]
)
def update_scatter_chart(selected_site, payload_range):
    lower, upper = payload_range  # Unpack the selected payload range (min and max values)
    
    # Filter the data to include only the selected payload range
    filtered_data = spacex_df[spacex_df['Payload Mass (kg)'].between(lower, upper)]
    
    # If 'All Sites' is selected, show data for all sites
    if selected_site == 'All Sites':
        fig = px.scatter(
            filtered_data,  # Use the filtered data based on payload range
            x="Payload Mass (kg)",  # X-axis: payload mass
            y="class",  # Y-axis: success/failure (class)
            color="Booster Version Category",  # Color points by booster version
            hover_data=['Launch Site'],  # Show launch site on hover
            title='Payload vs Launch Success for All Sites'  # Title of the chart
        )
    else:
        # If a specific site is selected, filter the data further by launch site
        site_data = filtered_data[filtered_data['Launch Site'] == selected_site]
        fig = px.scatter(
            site_data,  # Use the filtered data for the specific site
            x="Payload Mass (kg)",  # X-axis: payload mass
            y="class",  # Y-axis: success/failure (class)
            color="Booster Version Category",  # Color points by booster version
            hover_data=['Launch Site'],  # Show launch site on hover
            title=f'Payload vs Launch Success for Site {selected_site}'  # Title with the selected site
        )
    return fig  # Return the figure to update the chart

# Run the app
if __name__ == '__main__':
    app.run_server()

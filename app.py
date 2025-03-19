import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Create the Dash app
app = dash.Dash(__name__, title="Philippines Candidate Comparison Dashboard")

# Add this line here
server = app.server  # Expose the WSGI server

# Load the data
df = pd.read_csv('data/Pulse_Feb_Regional.csv')

# Define region groups
major_regions = ['PHILIPPINES (100%)', 'NCR (11%)', 'BALANCE LUZON (45%)', 'VISAYAS (20%)', 'MINDANAO (24%)']
detailed_regions = [col for col in df.columns if col not in ['Name'] + major_regions and not col.endswith('.1')]

# Define color scheme
candidate1_color = "#1e88e5"  # Blue
candidate2_color = "#e53935"  # Red

# App layout
app.layout = html.Div([
    html.H1("Philippines Candidate Comparison Dashboard", className="dashboard-title"),

    html.Div([
        html.Div([
            html.Label("Candidate 1:"),
            dcc.Dropdown(
                id='candidate1-dropdown',
                options=[{'label': name, 'value': name} for name in df['Name']],
                value=df['Name'][0],
                className="candidate1-dropdown"
            )
        ], className="dropdown-container"),

        html.Div([
            html.Label("Candidate 2:"),
            dcc.Dropdown(
                id='candidate2-dropdown',
                options=[{'label': name, 'value': name} for name in df['Name']],
                value=df['Name'][1],
                className="candidate2-dropdown"
            )
        ], className="dropdown-container"),

        html.Div([
            html.Label("View:"),
            dcc.RadioItems(
                id='view-selector',
                options=[
                    {'label': 'Major Regions', 'value': 'major'},
                    {'label': 'Detailed Regions', 'value': 'detailed'}
                ],
                value='major',
                className="view-selector"
            )
        ], className="dropdown-container")
    ], className="controls-container"),

    html.Div([
        html.H2("National Overview", className="section-title"),
        html.Div(id='national-overview', className="overview-container")
    ], className="section-container"),

    html.Div([
        html.H2("Regional Comparison", className="section-title"),
        dcc.Graph(id='regional-comparison-chart')
    ], className="section-container"),

    html.Div([
        html.H2("Advantage Map", className="section-title"),
        dcc.Graph(id='advantage-map-chart')
    ], className="section-container"),

    html.Div([
        html.P("Data source: Pulse February Regional Survey"),
        html.P("Values represent percentage support in each region")
    ], className="footer")
], className="dashboard-container")


# Callback for updating the overview
@app.callback(
    Output('national-overview', 'children'),
    [Input('candidate1-dropdown', 'value'),
     Input('candidate2-dropdown', 'value')]
)
def update_overview(candidate1, candidate2):
    # Get national data for both candidates
    candidate1_data = df[df['Name'] == candidate1].iloc[0]
    candidate2_data = df[df['Name'] == candidate2].iloc[0]

    # National percentages
    candidate1_national = candidate1_data['PHILIPPINES (100%)']
    candidate2_national = candidate2_data['PHILIPPINES (100%)']

    # Find top regions for each candidate
    top_regions1 = []
    top_regions2 = []

    # Get all region columns (excluding Name and national)
    region_cols = [col for col in df.columns if col != 'Name' and col != 'PHILIPPINES (100%)']

    # Get top 3 regions for candidate 1
    c1_regions = [(region, candidate1_data[region]) for region in region_cols]
    c1_regions.sort(key=lambda x: x[1], reverse=True)
    top_regions1 = c1_regions[:3]

    # Get top 3 regions for candidate 2
    c2_regions = [(region, candidate2_data[region]) for region in region_cols]
    c2_regions.sort(key=lambda x: x[1], reverse=True)
    top_regions2 = c2_regions[:3]

    # Calculate national difference
    difference = candidate1_national - candidate2_national

    # Create overview div
    overview = html.Div([
        html.Div([
            html.Div([
                html.H3(candidate1, style={'color': candidate1_color, 'fontWeight': 'bold'}),
                html.P(f"{candidate1_national}%", className="national-percentage"),
                html.P("Top Performing Regions:", className="top-regions-title"),
                html.Ul([
                    html.Li(f"{region}: {percentage}%") for region, percentage in top_regions1
                ], className="top-regions-list")
            ], className="candidate-overview candidate1-overview"),

            html.Div([
                html.H3(candidate2, style={'color': candidate2_color, 'fontWeight': 'bold'}),
                html.P(f"{candidate2_national}%", className="national-percentage"),
                html.P("Top Performing Regions:", className="top-regions-title"),
                html.Ul([
                    html.Li(f"{region}: {percentage}%") for region, percentage in top_regions2
                ], className="top-regions-list")
            ], className="candidate-overview candidate2-overview")
        ], className="candidates-container"),

        html.Div([
            html.P([
                "National Difference: ",
                html.Span(
                    f"{abs(difference):.1f}% in favor of {candidate1 if difference > 0 else candidate2}",
                    style={
                        'color': candidate1_color if difference > 0 else candidate2_color,
                        'fontWeight': 'bold'
                    }
                )
            ], className="difference-text")
        ], className="difference-container")
    ])

    return overview


# Callback for updating the regional comparison chart
@app.callback(
    Output('regional-comparison-chart', 'figure'),
    [Input('candidate1-dropdown', 'value'),
     Input('candidate2-dropdown', 'value'),
     Input('view-selector', 'value')]
)
def update_comparison_chart(candidate1, candidate2, view):
    # Get data for both candidates
    candidate1_data = df[df['Name'] == candidate1].iloc[0]
    candidate2_data = df[df['Name'] == candidate2].iloc[0]

    # Choose regions based on view
    if view == 'major':
        regions = major_regions
    else:
        regions = detailed_regions

    # Prepare data for chart
    chart_data = {
        'Region': [],
        candidate1: [],
        candidate2: []
    }

    for region in regions:
        chart_data['Region'].append(region)
        chart_data[candidate1].append(candidate1_data[region])
        chart_data[candidate2].append(candidate2_data[region])

    # Create DataFrame
    chart_df = pd.DataFrame(chart_data)

    # Create figure
    fig = go.Figure()

    # Add bars for candidate 1
    fig.add_trace(go.Bar(
        y=chart_df['Region'],
        x=chart_df[candidate1],
        name=candidate1,
        orientation='h',
        marker=dict(color=candidate1_color),
        text=chart_df[candidate1].apply(lambda x: f"{x:.1f}%"),
        textposition='auto'
    ))

    # Add bars for candidate 2
    fig.add_trace(go.Bar(
        y=chart_df['Region'],
        x=chart_df[candidate2],
        name=candidate2,
        orientation='h',
        marker=dict(color=candidate2_color),
        text=chart_df[candidate2].apply(lambda x: f"{x:.1f}%"),
        textposition='auto'
    ))

    # Update layout
    fig.update_layout(
        title="Regional Support Comparison",
        height=600,
        barmode='group',
        xaxis=dict(title="Support Percentage (%)", range=[0, 100]),
        yaxis=dict(title="Region"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


# Callback for updating the advantage map chart
@app.callback(
    Output('advantage-map-chart', 'figure'),
    [Input('candidate1-dropdown', 'value'),
     Input('candidate2-dropdown', 'value'),
     Input('view-selector', 'value')]
)
def update_advantage_chart(candidate1, candidate2, view):
    # Get data for both candidates
    candidate1_data = df[df['Name'] == candidate1].iloc[0]
    candidate2_data = df[df['Name'] == candidate2].iloc[0]

    # Choose regions based on view
    if view == 'major':
        regions = major_regions
    else:
        regions = detailed_regions

    # Prepare data for chart
    chart_data = {
        'Region': [],
        'Difference': [],
        'Color': [],
        'Text': []
    }

    for region in regions:
        diff = candidate1_data[region] - candidate2_data[region]
        chart_data['Region'].append(region)
        chart_data['Difference'].append(diff)
        chart_data['Color'].append(candidate1_color if diff >= 0 else candidate2_color)

        favored = candidate1 if diff >= 0 else candidate2
        chart_data['Text'].append(f"{abs(diff):.1f}% advantage for {favored}")

    # Create DataFrame
    chart_df = pd.DataFrame(chart_data)

    # Create figure
    fig = go.Figure()

    # Add bars
    fig.add_trace(go.Bar(
        y=chart_df['Region'],
        x=chart_df['Difference'],
        orientation='h',
        marker=dict(color=chart_df['Color']),
        text=chart_df['Text'],
        textposition='auto',
        name="Advantage"
    ))

    # Update layout
    fig.update_layout(
        title="Regional Advantage Map",
        height=600,
        xaxis=dict(
            title="Advantage (%)",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            range=[-60, 60]
        ),
        yaxis=dict(title="Region"),
        showlegend=False
    )

    return fig


# Add custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Philippines Candidate Comparison Dashboard</title>
        {%metas%}
        {%favicon%}
        {%css%}
        <style>
            .dashboard-container {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .dashboard-title {
                text-align: center;
                margin-bottom: 30px;
                color: #333;
            }
            .controls-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                margin-bottom: 30px;
                gap: 20px;
            }
            .dropdown-container {
                flex: 1;
                min-width: 250px;
            }
            .candidate1-dropdown .Select--single > .Select-control {
                background-color: #e3f2fd;
                border-color: #1e88e5;
            }
            .candidate2-dropdown .Select--single > .Select-control {
                background-color: #ffebee;
                border-color: #e53935;
            }
            .section-container {
                margin-bottom: 40px;
                padding: 20px;
                border-radius: 5px;
                background-color: #f9f9f9;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .section-title {
                margin-top: 0;
                border-bottom: 1px solid #ddd;
                padding-bottom: 10px;
                color: #444;
            }
            .overview-container {
                margin-top: 20px;
            }
            .candidates-container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
            }
            .candidate-overview {
                flex: 1;
                min-width: 300px;
                padding: 15px;
                border-radius: 5px;
            }
            .candidate1-overview {
                background-color: rgba(30, 136, 229, 0.1);
            }
            .candidate2-overview {
                background-color: rgba(229, 57, 53, 0.1);
            }
            .national-percentage {
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }
            .top-regions-title {
                font-weight: bold;
                margin-bottom: 5px;
            }
            .top-regions-list {
                margin-top: 5px;
                padding-left: 20px;
            }
            .difference-container {
                margin-top: 20px;
                padding: 15px;
                border-top: 1px solid #ddd;
                text-align: center;
            }
            .difference-text {
                font-size: 1.2em;
            }
            .footer {
                margin-top: 20px;
                text-align: center;
                color: #777;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

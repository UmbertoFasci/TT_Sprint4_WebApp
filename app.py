import streamlit as st
import pandas as pd
import plotly.express as px

# load vehicles_us.csv
vehicles = pd.read_csv("vehicles_us.csv")

# Data Preprocessing
# Drop missing values from model_year, and cylinders
vehicles = vehicles.dropna(subset=['model_year', 'cylinders'])

# Fill NA paint_color
vehicles['paint_color'] = vehicles['paint_color'].fillna('unknown')

# Fill NA odomerter
vehicles['odometer'] = vehicles['odometer'].fillna(vehicles['odometer'].median())

# Fill NA is_4wd
vehicles['is_4wd'] = vehicles['is_4wd'].fillna(0)

vehicles = vehicles.astype({'is_4wd': 'int64', 'odometer': 'int64', 'cylinders': 'int64', 'model_year': 'int64'})

vehicles = vehicles[vehicles['model'].str.lower() != 'chevrolet silverado']

# Standardize Ford F-XXX
vehicles['model'].replace('ford f150', 'ford f-150', inplace=True)
vehicles['model'].replace('ford f250', 'ford f-250', inplace=True)
vehicles['model'].replace('ford f350', 'ford f-350', inplace=True)

vehicles['date_posted'] = pd.to_datetime(vehicles['date_posted'])


st.set_page_config(page_title="U. Fasci - DS Sprint 4 Submission", layout="wide")

### Create sidebar
with st.sidebar:

    st.title("Vehicle Data Price Analysis")
    st.subheader("By Umberto Fasci")
    st.markdown("""Utilizing the :red[vehicle data] provided by TripleTen. The following analysis was performed. \
                """)


col1,col2 = st.columns(2)

with col1:
    st.header('Distribution of Vehicle Prices')
    st.write("""
            This visualization provides insights into the 
            range and spread of vehicle prices within the vehicle dataset. By examining this distribution,
            we can identify common price ranges for different types of vehicles, and detect any patterns
            or anomalies. \n
            \n
            When inspecting the histogram we can see a right-skewed distribution expressing most price values
            below \$10k, and a median price value of \$9,000.
            """)
    
    # Calculate summary statistics for the 'price' variable
    price_summary = vehicles['price'].describe(percentiles=[0.25, 0.5, 0.75]).to_frame().T

    # Rounding for display
    price_summary = price_summary.round(2)

    # Select key statistics to display
    price_summary = price_summary[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]

    # Renaming columns for better readability
    price_summary = price_summary.rename(columns={
        'mean': 'Mean',
        'std': 'Std Dev',
        'min': 'Min',
        '25%': '25th Pctl',
        '50%': 'Median',
        '75%': '75th Pctl',
        'max': 'Max'
    })

    # Index not needed when only looking at price stats
    price_summary.index = ['']

    # Streamlit code to display the summary statistics
    st.subheader('Summary Statistics for Vehicle Prices')

    # Style the dataframe for Streamlit
    st.table(price_summary.style.format(precision=2).set_table_styles([
        {'selector': 'thead th', 'props': [('font-weight', 'bold'),
                                           ('font-size', '12px')]},
        {'selector': 'tbody td', 'props': [('font-size', '12px')]}
    ]))
    st.write("""
             Looking at a box plot of the data will better reveal the distribution
             and it's outliers. Check the box below to view the associated box plot.
             Once activated, we can see the IQR appropriately reflected, and several outlying data.
             One outlier expresses a price of :red[$375K]!
             """)

# Create a histogram of car prices
def create_histogram(show_marginal):
    fig = px.histogram(vehicles, x='price', nbins=45, 
                       title='Distribution Plot of Vehicle Prices',
                       labels={'price': 'Price ($)'},
                       color_discrete_sequence=['#ff6e54'],
                       marginal='box' if show_marginal else None,  # For the checkbox!
                       height=500,
                       width=800)

    fig.update_layout(
        xaxis_title='Price ($)',
        yaxis_title='Vehicle Count',
        title_font_size=18,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig

show_marginal = st.checkbox('Show Marginal Box Plot', value=False)
fig = create_histogram(show_marginal)

# Using col2 instead of st for layout purposes
col2.plotly_chart(fig)

st.divider()

st.header('Price vs Year and Outliers')
st.write("""
        This scatterplot demonstrates the relationship between price and model_year. However,
        there is interpretation interference due to the several outlying date on both ends of
        the analysis. The data between the years 1900 and 1950 is sparse and only serves
        to stretch the year range.  \n
        \n
        Similarly, there are several large price values that are really only contributing to
        making the rest of values more difficult to interpret. In this case, the largest price
        value at :red[$375K] is pointed out with a :red[*].
        """)

st.write("""
        The date range that should be disregarded for the purposes of this analysis has
        also been higlighted in red.
        """)

# Step 1: Create scatterplot using Plotly Express
fig = px.scatter(
    vehicles,
    x='model_year',
    y='price',
    title='Scatterplot of Price vs Year',
    labels={'model_year': 'Year', 'price': 'Price ($)'},
    color='price',
    color_continuous_scale=px.colors.sequential.Blackbody,
    size_max=20,
    opacity=0.7,
    height=600,
    width=800
)

fig.add_shape(
    # Rectangle
    type='rect',
    x0=1900,  # Start of the highlight (year 1908)
    y0=0,  # Start of the y-axis range (can adjust based on your data range)
    x1=1949,  # End of the highlight (year 1948)
    y1=vehicles['price'].max(),  # End of the y-axis range (maximum price in data)
    line=dict(color='red', width=2),  # Outline color and width
    fillcolor='LightSalmon',  # Fill color for the rectangle
    opacity=0.3  # Transparency of the rectangle
)

fig.add_annotation(
    x=vehicles.loc[vehicles['price'] == 375000, 'model_year'].values[0],  # Model year of the point
    y=375000,  # Price of the point
    text="*",  # Annotation text
    showarrow=True,  # Show an arrow pointing to the point
    arrowhead=6,  # Style of the arrowhead
    ax=0,  # x-offset for the arrow's starting point
    ay=-30,  # y-offset for the arrow's starting point
    font=dict(size=30, color='red')  # Font size and color for the annotation
)

# Update layout for better visualization
fig.update_layout(
    title_font_size=18,
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=40, r=40, t=60, b=40)
)


# Display scatterplot in Streamlit
st.plotly_chart(fig, use_container_width=True)

st.write("""
        To visualize the affect of removing these outlying data and identifying trends, here
        is a facetted box plot group representing price vs decade. 
        """)

# Create a new column for the decade
vehicles['model_decade'] = (vehicles['model_year'] // 10) * 10
vehicles = vehicles[vehicles['model_decade'] >= 1950] 

# Calculate the IQR and filter out outliers
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

vehicles_filtered = vehicles.groupby('model_decade').apply(remove_outliers, 'price').reset_index(drop=True)

# Create the facetted box plot with filtered data
fig = px.box(vehicles_filtered, x='model_decade', y='price', 
             title='Price Distribution by Decade (1950 and Beyond)',
             labels={'model_decade': 'Decade', 'price': 'Price ($)'},
             color='model_decade',
             color_discrete_map={
                 2010: '#003f5c',
                 2000: '#374c80',
                 1990: '#7a5195',
                 1980: '#bc5090',
                 1970: '#ef5675',
                 1960: '#ff764a',
                 1950: '#ffa600'
             },
             facet_col='model_decade',  # Facet by decade
             facet_col_wrap=7,
             template='plotly_white')

# Update layout for better visualization
fig.update_layout(
    yaxis_title='Price ($)',
    title_font_size=20,
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
    height=600,  # Increase plot height for better readability
    width=1000,  # Increase plot width for better readability
    margin=dict(l=50, r=50, t=100, b=100),
)

for axis in fig.layout:
    if axis.startswith('xaxis') and 'model_decade=' not in axis:
        fig.layout[axis].title.text = ''  # Remove the title
        fig.layout[axis].showticklabels = False 

fig.update_xaxes(matches=None)  # Ensure x-axes are independent for each facet

# Show the plot
st.plotly_chart(fig)

st.write("""
         By removing the outlying data and visualizing the price ranges by decade.
         The picture of this trend becomes clear.
         \n
         Prices were at the highest in the 50s and tended to decrease as the years came along.
         Increasing prices were being experienced when the 2000s came along, and have continued to grow
         in the 2010s.
         """)
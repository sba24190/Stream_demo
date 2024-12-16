pip install plotly
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="Agricultural Data Dashboard",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the data
file_path = 'C:/Users/diarm/OneDrive/Documents/CCT MSC Sem1/Programming for Data Analytics/CA/msc-da-sept-24-sem-1-ca2-sba24190/combined_data.csv'
df = pd.read_csv(file_path)

# Define the heatmap function
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
        y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
        x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
        color=alt.Color(f'max({input_color}):Q', legend=None, scale=alt.Scale(scheme=input_color_theme)),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.25),
    ).properties(width=900).configure_axis(labelFontSize=12, titleFontSize=12)
    return heatmap

# Define the choropleth function
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(
        input_df, locations=input_id, color=input_column, locationmode="country names",
        color_continuous_scale=input_color_theme, animation_frame='Year', scope="europe",
        labels={'Cereal_Yield': 'Cereal Yield'}
    )
    choropleth.update_layout(
        template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0), height=600
    )
    return choropleth

# Calculate the percentage of countries with cereal yield over 5000kg per hectare
def calculate_percentage(df, year, threshold=5000):
    year_data = df[df['Year'] == year]
    above_threshold = year_data[year_data['Cereal_Yield'] > threshold].shape[0]
    total_countries = year_data.shape[0]
    percentage_above_threshold = (above_threshold / total_countries) * 100
    return percentage_above_threshold

# Define the donut chart function
def make_donut_chart(percentage, input_text, chart_color):
    source = pd.DataFrame({
        'Topic': [input_text, ''],
        '% value': [percentage, 100 - percentage]
    })
    source_bg = pd.DataFrame({
        'Topic': [input_text, ''],
        '% value': [100, 0]
    })
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value:Q",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(domain=[input_text, ''], range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{percentage:.1f} %'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value:Q",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(domain=[input_text, ''], range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    return plot_bg + plot + text

# Function to format numbers
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# Sidebar for year selection
with st.sidebar:
    st.title('🚜 EU Agriculture Dashboard')
    year_list = list(df['Year'].unique())[::-1]
    selected_year = st.selectbox('Select a year', year_list, index=len(year_list)-1)
    df_selected_year = df[df['Year'] == selected_year]

# Main layout with three columns
col = st.columns((1.5, 4.5, 2), gap='medium')

# Column 1: Gains/Losses
with col[0]:
    st.markdown('#### Gains/Losses')

    # Find highest and lowest cereal yield countries for the selected year
    highest_cereal_yield = df_selected_year.sort_values(by='Cereal_Yield', ascending=False).iloc[0]
    lowest_cereal_yield = df_selected_year.sort_values(by='Cereal_Yield').iloc[0]

    st.metric(label=highest_cereal_yield['Country Name'],
              value=f"{format_number(highest_cereal_yield['Cereal_Yield'])} kg/ha",
              delta=f"Highest Cereal Yield")

    st.metric(label=lowest_cereal_yield['Country Name'],
              value=f"{format_number(lowest_cereal_yield['Cereal_Yield'])} kg/ha",
              delta=f"Lowest Cereal Yield")
    
    st.markdown('#### States Migration')

    percentage_above_5000 = calculate_percentage(df_selected_year, selected_year)
    percentage_below_5000 = 100 - percentage_above_5000

    donut_chart_above_5000 = make_donut_chart(percentage_above_5000, 'Cereal Yield > 5000kg/ha', ['#29b5e8', '#155F7A'])
    donut_chart_below_5000 = make_donut_chart(percentage_below_5000, 'Cereal Yield < 5000kg/ha', ['#29b5e8', '#155F7A'])

    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('Above 5000kg/ha')
        st.altair_chart(donut_chart_above_5000)
        st.write('Below 5000kg/ha')
        st.altair_chart(donut_chart_below_5000)

# Column 2: Heatmap and Choropleth map
with col[1]:
    st.markdown('#### Cereal Yield')

    # Create and display the choropleth map
    choropleth = make_choropleth(df, 'Country Name', 'Cereal_Yield', 'viridis')
    st.plotly_chart(choropleth, use_container_width=True)
    
    # Create and display the heatmap
    heatmap = make_heatmap(df, 'Year', 'Country Name', 'Cereal_Yield', 'viridis')
    st.altair_chart(heatmap, use_container_width=True)

# Column 3: Top Countries and About section
with col[2]:
    st.markdown('#### Top Countries')

    # Sort dataframe for the selected year by cereal yield
    df_selected_year_sorted = df_selected_year.sort_values(by='Cereal_Yield', ascending=False)

    st.dataframe(df_selected_year_sorted,
                 column_order=("Country Name", "Cereal_Yield"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "Country Name": st.column_config.TextColumn(
                        "Country",
                    ),
                    "Cereal_Yield": st.column_config.ProgressColumn(
                        "Cereal Yield (kg/ha)",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.Cereal_Yield),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [World Bank](https://databank.worldbank.org/source/world-development-indicators/Type/TABLE/preview/on).
            - :orange[**Highest/Lowest Yield**]: countries with high/low cereal yield for selected year
            - :orange[**Countries with Yield above/below 5000kg/ha**]: percentage of countries with yield above/below  5,000kg/ha
            ''')

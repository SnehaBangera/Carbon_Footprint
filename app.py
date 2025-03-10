import streamlit as st
from src.carbon_utils import load_emission_factors, categorize_emissions, send_email_smtp
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

# Hide Streamlit's default UI elements
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;} /* Hides the hamburger menu */
    footer {visibility: hidden !important;} /* Hides the footer */
    header {visibility: hidden;} /* Hides the Streamlit header */
    .viewerBadge_container__1QSob {display: none;} /* Hides the "Fork" button */
    .st-cf, .st-c0 {display: none;} /* Hides Streamlit branding and profile badge */
    
    /* Hides custom footer text */
    div.block-container div:first-child div[data-testid="stMarkdownContainer"] p {
        visibility: hidden;
        height: 0px;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.title("🌍 Carbon Footprint Calculator")

def carbon_footprint_calculator():
    # Load emission factors
    EMISSION_FACTORS, data = load_emission_factors()

    # Streamlit UI
    st.title("Carbon Footprint Calculator")

    # Select country
    st.subheader("Your country")
    country = st.selectbox("Select your country", list(EMISSION_FACTORS.keys()))

    # Input values
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Daily commute distance in KM")
        distance = st.slider("Distance", 0.0, 100.0, key="distance_input")

        st.subheader("Monthly electricity consumption in KWH")
        electricity = st.slider("Electricity", 0.0, 1000.0, key="electricity_input")

    with col2:
        st.subheader("Number of meals per day")
        diet = st.number_input("Diet", 0, key="diet_input")

        st.subheader("Daily waste in KG")
        waste = st.slider("Waste", 0.0, 100.0, key="waste_input")

    # Normalize input values to yearly
    distance *= 365  
    electricity *= 12  
    diet *= 365  
    waste *= 52  

    # Calculate emissions
    transportation_emissions = distance * EMISSION_FACTORS[country]["Transportation"] / 1000
    electricity_emissions = electricity * EMISSION_FACTORS[country]["Electricity"] / 1000
    diet_emissions = diet * EMISSION_FACTORS[country]["Diet"] / 1000
    waste_emissions = waste * EMISSION_FACTORS[country]["Waste"] / 1000

    total_emissions = round(transportation_emissions + electricity_emissions + diet_emissions + waste_emissions, 2)

    # Get country's average emissions from CSV
    country_data = data[data['Country'] == country]
    total_emission_from_csv = (
        country_data[['Transportation (kg CO2 per km)', 'Electricity (kg CO2 per kWh)', 'Diet (kg CO2 per meal)', 'Waste (kg CO2 per kg)']]
        .sum(axis=1)
        .values[0]
        if not country_data.empty
        else 0
    )

    # Categorize emissions
    category, message = categorize_emissions(total_emissions, country, total_emission_from_csv)

    # Calculate emissions when button is clicked
    if st.button("Calculate CO2 Emission"):
        st.session_state.results = {
            "transportation_emissions": transportation_emissions,
            "electricity_emissions": electricity_emissions,
            "diet_emissions": diet_emissions,
            "waste_emissions": waste_emissions,
            "total_emissions": total_emissions,
            "category": category,
            "message": message,
            "country_emissions": total_emission_from_csv,
        }

    # Display results
    if "results" in st.session_state:
        results = st.session_state.results

        st.header("Results")

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Carbon emission by category")
            st.info(f"Transportation: {results['transportation_emissions']} tons")
            st.info(f"Electricity: {results['electricity_emissions']} tons")
            st.info(f"Diet: {results['diet_emissions']} tons")
            st.info(f"Waste: {results['waste_emissions']} tons")

            fig, ax = plt.subplots()
            ax.bar(
                ['Transportation', 'Electricity', 'Diet', 'Waste'],
                [results['transportation_emissions'], results['electricity_emissions'], results['diet_emissions'], results['waste_emissions']],
                color=['blue', 'green', 'orange', 'red']
            )
            ax.set_xlabel('Category')
            ax.set_ylabel('Emissions (tons)')
            ax.set_title('Carbon Emissions by Category')
            st.pyplot(fig)

        with col4:
            st.subheader("Total carbon emissions")
            st.info(f"{results['total_emissions']} tons")
            st.warning(results['message'])

            fig = px.pie(
                names=['Transportation', 'Electricity', 'Diet', 'Waste'],
                values=[results['transportation_emissions'], results['electricity_emissions'], results['diet_emissions'], results['waste_emissions']],
                title="Proportion of Total Emissions by Category"
            )
            st.plotly_chart(fig)

        st.subheader("Country's Total Emissions from CSV")
        st.info(f"{results['country_emissions']} tons")

        # Email Report Section
        st.header("Email Report")
        user_email = st.text_input("Enter your email to receive the report")

        if st.button("Send Report via Email"):
            if user_email:
                # Generate report image
                image_path = "carbon_report.png"
                fig, ax = plt.subplots()
                ax.bar(
                    ['Transportation', 'Electricity', 'Diet', 'Waste'],
                    [results['transportation_emissions'], results['electricity_emissions'], results['diet_emissions'], results['waste_emissions']],
                    color=['blue', 'green', 'orange', 'red']
                )
                ax.set_xlabel('Category')
                ax.set_ylabel('Emissions (tons)')
                ax.set_title('Carbon Emissions by Category')
                plt.savefig(image_path)

                # Send email
                success = send_email_smtp(
                    user_email, 
                    "Your Carbon Footprint Report",
                    results,
                    image_path
                )

                if success:
                    st.success("Report sent successfully!")
                else:
                    st.error("Failed to send email.")

carbon_footprint_calculator()




import streamlit as st
import pandas as pd
import os

# Get the folder where this script lives, so file paths always work
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

st.title("South America Property Search")

# --- Load real data ---
@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(SCRIPT_DIR, "properties_clean.csv"))
    return df

df = load_data()

# --- Country Summaries ---
country_info = {
    "Argentina": {
        "Friendliness": "Argentina has a strong European cultural influence and is welcoming to foreigners, though economic instability and inflation can make financial planning unpredictable.",
        "Quality of Life": "Buenos Aires rivals European capitals for culture, dining, and nightlife, while Mendoza offers world-class wine country and outdoor adventures at bargain prices.",
        "Healthcare": "Argentina has a well-regarded public and private healthcare system, with many English-speaking doctors in Buenos Aires.",
        "Why Move": "The sophistication of Buenos Aires, incredible steak and wine, tango culture, and Patagonian wilderness offer a rich, affordable lifestyle.",
        "Why Not Move": "Chronic inflation and currency instability make long-term financial planning very difficult, and the economy goes through regular crises.",
    },
    "Brasil": {
        "Friendliness": "Brazil is warm and welcoming to foreigners, with a vibrant culture, though language barrier (Portuguese, not Spanish) and safety concerns in some urban areas require awareness.",
        "Quality of Life": "Brazil offers stunning beaches, lively music and dance culture, incredible biodiversity, and a relaxed lifestyle — from cosmopolitan São Paulo to tropical Bahia.",
        "Healthcare": "Brazil has a universal public healthcare system (SUS) and good private hospitals in major cities at reasonable costs.",
        "Why Move": "The natural beauty, warm culture, year-round tropical weather, and relatively low cost of living outside major cities make Brazil a vibrant place to live.",
        "Why Not Move": "The primary language is Portuguese (not Spanish), crime rates in major cities are a concern, and bureaucracy for foreign residents can be challenging.",
    },
    "México": {
        "Friendliness": "Mexico has a large and well-established American expat community, especially in areas like Lake Chapala, San Miguel de Allende, and the Riviera Maya, making it one of the easiest transitions.",
        "Quality of Life": "Mexico offers incredible food, rich history, beautiful beaches, mountain towns, and a cost of living that can be 50-70% less than the US, all in a nearby time zone.",
        "Healthcare": "Mexico has excellent private healthcare in major cities and medical tourism hubs, with many US-trained doctors at a fraction of US prices.",
        "Why Move": "Proximity to the US (easy flights home), huge expat communities, familiar culture, great food, and affordable living make Mexico the #1 destination for American expats.",
        "Why Not Move": "Security concerns vary significantly by region, and while expat areas are generally safe, cartel activity in some states is a real concern to research carefully.",
    },
}

# --- Search Filters ---
st.sidebar.header("Search Filters")

all_countries = sorted(df["Country"].unique().tolist())
country = st.sidebar.multiselect(
    "Country",
    ["All"] + all_countries,
    default=["All"]
)

price_range = st.sidebar.slider("Price Range ($)", 5000, 1000000, (50000, 300000), step=5000)
min_sqft = st.sidebar.number_input("Minimum Size (sq ft)", value=500, step=100)

property_type = st.sidebar.multiselect(
    "Property Type",
    ["house", "apartment"],
    default=["house", "apartment"]
)

max_city_dist = st.sidebar.slider("Max distance to city of 10,000+ (miles)", 1, 100, 50)
max_hospital_dist = st.sidebar.slider("Max distance to hospital (miles)", 1, 100, 30)
max_airport_dist = st.sidebar.slider("Max distance to airport (miles)", 1, 200, 75)
near_americans = st.sidebar.checkbox("Near other American expats")

# --- Filter the data ---
selected_countries = all_countries if "All" in country else country

filtered = df[
    (df["Country"].isin(selected_countries)) &
    (df["Price"] >= price_range[0]) &
    (df["Price"] <= price_range[1]) &
    (df["SqFt"] >= min_sqft) &
    (df["Type"].isin(property_type)) &
    (df["Miles to City"] <= max_city_dist) &
    (df["Miles to Hospital"] <= max_hospital_dist) &
    (df["Miles to Airport"] <= max_airport_dist)
]

if near_americans:
    filtered = filtered[filtered["Expat Community"] == True]

# --- Display Results ---
st.subheader(f"Results: {len(filtered):,} properties found")

if len(filtered) == 0:
    st.info("No properties match your filters. Try adjusting your search criteria.")
else:
    # Cap display at 100 to keep the app responsive
    if len(filtered) > 100:
        st.write(f"Showing first 100 of {len(filtered):,} results. Narrow your filters to see fewer results.")

    display = filtered.head(100)

    for _, row in display.iterrows():
        rooms_text = f" | {int(row['Rooms'])} rooms" if pd.notna(row['Rooms']) else ""
        title_text = row['Title'] if pd.notna(row['Title']) else f"{row['Type'].title()} in {row['City']}"

        with st.expander(f"📍 {row['City']}, {row['Country']} — ${row['Price']:,.0f} | {row['SqFt']:,} sq ft{rooms_text}"):
            st.write(f"**{title_text}**")

            col1, col2, col3 = st.columns(3)
            col1.metric("Type", row["Type"].title())
            col2.metric("Size", f"{row['SqFt']:,} sq ft")
            col3.metric("Rooms", int(row["Rooms"]) if pd.notna(row["Rooms"]) else "N/A")

            col4, col5, col6 = st.columns(3)
            col4.metric("Nearest City (10k+)", f"{row['Miles to City']} mi")
            col5.metric("Nearest Hospital", f"{row['Miles to Hospital']} mi")
            col6.metric("Nearest Airport", f"{row['Miles to Airport']} mi")

            expat_status = "✅ Yes" if row["Expat Community"] else "❌ No"
            st.write(f"**American Expat Community Nearby:** {expat_status}")

            if pd.notna(row["Link"]):
                st.markdown(f"🔗 [View Property Listing]({row['Link']})")

            # Country summaries
            info = country_info.get(row["Country"])
            if info:
                st.markdown("---")
                st.markdown(f"**🏛️ Friendliness for Americans:** {info['Friendliness']}")
                st.markdown(f"**🌴 Quality of Life:** {info['Quality of Life']}")
                st.markdown(f"**🏥 Healthcare:** {info['Healthcare']}")
                st.markdown(f"**👍 Why move here:** {info['Why Move']}")
                st.markdown(f"**👎 Why not move here:** {info['Why Not Move']}")

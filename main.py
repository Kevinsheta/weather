# main.py
import streamlit as st
import os
from streamlit_cookies_manager import EncryptedCookieManager
import json
from database import *
from weather import *
from visualization import *
from notification import *
from map import *
from news import *
from ui import *

# Set up cookies manager.
cookie_password = os.environ.get("COOKIE_PASSWORD", "default_fallback_password")
cookies= EncryptedCookieManager(prefix='2', password= cookie_password)
if not cookies.ready():
    st.stop() # Wait until the cookies are ready

# Handle exception when accessing cookies
try:
    cookie_history = json.loads(cookies.get('search_history', '[]'))  # Use get() with default value
except Exception as e:
    st.error(f"Failed to load cookies: {e}")
    cookie_history = []

if 'search_history' not in st.session_state:
    st.session_state['search_history']= cookie_history

# Save the (updated) history back into cookies
def update_cookies(history):
    try:
        cookies['search_history'] = json.dumps(history)
        # cookies.save()  # Make sure cookies are saved after modification
    except Exception as e:
        st.error(f"Error saving cookies: {e}")

def save_history(city):
    # Prevent duplicates
    if city in [entry["City"] for entry in st.session_state['search_history']]:
        return  # City is already in history, no need to add again

    # Add valid city to history
    st.session_state['search_history'].insert(0, {"City": city})
    st.session_state['search_history'] = st.session_state['search_history'][:10]  # Keep last 10 searches

    update_cookies(st.session_state['search_history'])  # Save updated history

# Save search to history
# def save_history(city, start_date, end_date):
#     # Check for duplicates
#     for entry in st.session_state['search_history']:
#         if (entry["City"] == city and entry["Start Date"] == str(start_date) and entry["End Date"] == str(end_date)):
#             # st.warning("This search is already in history.")
#             return
    
#     # Update Weather Data structure (remove icon_path and add relevant fields)
#     new_entry= {
#         "City": city,
#         "Start Date": str(start_date),
#         "End Date": str(end_date),
#         "Timestamp": datetime.now().strftime("%H:%M:%S")
#     }
#     st.session_state['search_history'].insert(0, new_entry)
#     st.session_state['search_history']= st.session_state['search_history'][:10]

#     update_cookies(st.session_state['search_history'])

# Display search history
# def display_history():
#     if st.session_state['search_history']:
#         with st.sidebar:
#             st.markdown("### Search History")
#             df = pd.DataFrame(st.session_state['search_history'])

#             gb = GridOptionsBuilder.from_dataframe(df[["City", "Start Date", "End Date", "Timestamp"]])
#             gb.configure_selection(selection_mode='single', use_checkbox=True)
#             gridOptions = gb.build()

#             # Render the AgGrid
#             grid_response = AgGrid(
#                 df[["City", "Start Date", "End Date", "Timestamp"]],
#                 gridOptions=gridOptions,
#                 update_mode=GridUpdateMode.SELECTION_CHANGED,
#                 height=250,
#                 theme='streamlit'
#             )

#         # Handle selection
#         selected_rows = grid_response.get("selected_rows", [])
#         if selected_rows:
#             selected_city = selected_rows[0]["City"].strip()

#             # ✅ Only update if city changes
#             if selected_city and selected_city != st.session_state.get("city_input", ""):
#                 st.session_state["city_input"] = selected_city
#                 st.session_state["weather_needs_update"] = True
#                 st.session_state["weather_updated"] = False  # Ensure update happens
#                 st.sidebar.success(f"✅ Weather updated for: {selected_city}")
#                 st.rerun()

#     else:
#         st.sidebar.info("No search history available.")

# Clear search history
def clear_history():
    st.session_state['search_history']= []
    update_cookies(st.session_state['search_history'])

    # Re-add detected location after clearing history
    # detected_city = fetch_user_location()
    save_history(st.session_state["city_input"])

    st.sidebar.success("Search history cleared.")
    # st.rerun()  # Ensure UI updates immediately



def main():
    
    # initialize_histoy_file() # Ensure history file exists
    
    if 'map_click' not in st.session_state:
        st.session_state['map_click']= None

    if "view" not in st.session_state:
        st.session_state["view"] = "Weather Data"

    if "city_input" not in st.session_state:
        st.session_state["city_input"] = ""
        # Save the detected city into the search history
        save_history(st.session_state["city_input"])
    
    if "weather_needs_update" not in st.session_state:
        st.session_state["weather_needs_update"] = True  # Initialize to True to fetch data on first load
    

    # Sidebar: Search for another city
    st.sidebar.title("🔍 Search Another City")
    search_city = st.sidebar.text_input("Enter city name:", placeholder="E.g., Tokyo, Berlin")
    
    # Ensure search history exists
    if "search_history" not in st.session_state:
        st.session_state["search_history"] = []

    # Ensure weather updates when a new city is selected
    # if st.session_state.get("weather_needs_update", False):
    #     st.session_state["weather_needs_update"] = False  # Reset flag AFTER updating weather data
    #     st.rerun() 
    
    
    # Handle user input from the sidebar
    if search_city and search_city != st.session_state.get("city_input", ""):      
        st.session_state["city_input"] = search_city
        st.session_state["weather_needs_update"] = True
        # Save search history immediately after search
        save_history(search_city)
        st.sidebar.success(f"✅ Showing weather for: {search_city}")
        
        # Set the active tab to "Weather Data"
        st.session_state["active_tab"] = 0  # Assuming "Weather Data" is the first tab (index 0)
        
        # time.sleep(2)
        st.rerun()

    # Search History Selection
    selected_city = st.sidebar.selectbox(
        "Search History",
        [entry["City"] for entry in st.session_state["search_history"]],
        index=None,
        key="city_history"
    )
   
    if selected_city and selected_city != st.session_state["city_input"]:
        st.session_state["city_input"] = selected_city
        st.session_state["weather_needs_update"] = True  #  Mark update needed
        
        # Clear success message from manual search
        # st.sidebar.empty()  # This removes any sidebar elements including previous success messages
        st.sidebar.success(f"✅ Showing weather for: {selected_city}")
        
        # Set the active tab to "Weather Data"
        st.session_state["active_tab"] = 0  # Assuming "Weather Data" is the first tab (index 0)
        
        # # time.sleep(2)
        # st.rerun()

    # Place the Clear History button in the sidebar using an on_click callback.
    st.sidebar.button("Clear Search History", on_click=clear_history) 

    # Set the default active tab if not already set
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = 0  # Default to "Weather Data"
        
    tab1, tab2, tab3, tab4, tab5= st.tabs(["🌦 Weather Data", "📊 Weather Data Visualization","🌍 Map ", "📰 Weather News", "📂 Weather Dataset"])
        
    # Display the detected/searched city on the main page
    with tab1:
        st.write("### 🌦 Weather Data Analysis")   
        st.write("##### 📍 Your Location")
        # city= st.text_input("Fetching your location details..", value=st.session_state["city_input"], disabled= True)
        
        # Main page input field
        city = st.text_input("Enter your city:", value=st.session_state["city_input"], placeholder="E.g., New York, Paris") 

        # Handle user input from the main page
        if city and city != st.session_state["city_input"]:
            st.session_state["city_input"] = city
            st.session_state["weather_needs_update"] = True
            save_history(city)
            # st.success(f"✅ Showing weather for: {city_main_input}")
            st.rerun()
        
        unit= st.radio('Select Temperature Unit:', ['Celsius (°C)', 'Fahrenheit (°F)'])
        if city and unit:
            unit= unit[0]
            with st.spinner("Just Wait!!"): 
                time.sleep(3)
            
            # if st.sidebar.button("Show Current Weather"):
            st.write(f"Fetching weather data for: {city}")

            weather_data= current_weather(city, unit)
            forecast_data= fetch_forecast_data(city)

            if weather_data and forecast_data:
                save_current_weather(city, weather_data)
                save_forecast_weather(city, forecast_data)

            # Fetch coordinates of the city
            lat, lon= fetch_coordinates(city)        

            if lat is not None and lon is not None and weather_data:
                # past_weather_data = fetch_past_weather_data(city)

                # display_weather_data(past_weather_data, city, unit, data_type= 'past')
                display_weather_data(forecast_data, city, unit, data_type= 'forecast')
                
                st.markdown("### <br>🌡️ 24-Hourly Data", unsafe_allow_html=True)  
                
                # Display notifications, cards, and other details
                hourly_data= fetch_weather_data(city, unit)
                if hourly_data:
                    # Display hourly weather data first
                    weather_card(hourly_data)

                    # Add spacing to separate sections
                    st.markdown("<br>", unsafe_allow_html=True) 

                    st.write('### <br>🚨 Weather Alert Message', unsafe_allow_html= True)
                    # Display notification below the hourly data
                    display_notification(city, hourly_data)

            else:
                st.error("Could not fetch weather data. Please check the city name or try again later.")
        else:
            st.info('Please enter a city name.')

    with tab2:
        st.write("### 📊 Weather Data Visualization")
        plot_weather_graph(city, unit)
    
    with tab3:
        st.write("### 🌍 Location Map")
        
        # Fetch coordinates again if city is entered
        lat, lon= fetch_coordinates(city) if city else (None, None)

        if city and lat is not None and lon is not None:
            display_map(city, lat, lon, weather_data)
        else:
            st.info("Please enter a city name to display the map.")

    with tab4:
        st.title("🌦 Weather News")
        with st.spinner("Fetching weather news..."):
            articles = fetch_weather_news()
        display_all_news(articles)
    
    with tab5:
        st.write("### 📂 Stored Weather Data")
        display_weather_tables()


    # Buttons for displaying and clearing history
    # if st.sidebar("Show History"):
    # display_history()

    # Place the Clear History button in the sidebar using an on_click callback.
    # st.sidebar.button("Clear Search History", on_click=clear_history)
    
    # Save cookies once at the end of the run to avoid duplicate component keys.
    cookies.save()


if __name__ == "__main__":
    main()
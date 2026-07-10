import pandas as pd
import pydeck as pdk

def render_flight_map(origin_coords, dest_coords):
    """Generates an interactive 3D PyDeck arc map for the flight route."""
    map_data = pd.DataFrame({
        "start_lat": [origin_coords['LATITUDE']], 
        "start_lon": [origin_coords['LONGITUDE']],
        "end_lat": [dest_coords['LATITUDE']], 
        "end_lon": [dest_coords['LONGITUDE']]
    })
    
    return pdk.Deck(
        map_style="dark",
        initial_view_state=pdk.ViewState(
            latitude=(origin_coords['LATITUDE'] + dest_coords['LATITUDE']) / 2,
            longitude=(origin_coords['LONGITUDE'] + dest_coords['LONGITUDE']) / 2,
            zoom=3, pitch=45,
        ),
        layers=[
            pdk.Layer(
                "ArcLayer", 
                data=map_data, 
                get_source_position=["start_lon", "start_lat"], 
                get_target_position=["end_lon", "end_lat"], 
                get_source_color=[200, 30, 0, 160], 
                get_target_color=[0, 200, 30, 160], 
                auto_highlight=True, 
                width_scale=2, 
                get_width=2
            )
        ]
    )
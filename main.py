from homeharvest import scrape_property

import folium
import pandas as pd
def main():
   

    properties = scrape_property(
        location="San Diego, CA",
        listing_type="sold",  # for_sale, for_rent, pending
        past_days=30
    )

    properties.to_csv("results.csv", index=False)
    print(f"Found {len(properties)} properties")




    # Drop rows where latitude or longitude are missing
    properties_clean = properties.dropna(subset=['latitude', 'longitude', 'sold_price', 'full_baths'])

    if not properties_clean.empty:
        # Get the average latitude and longitude to center the map
        center_lat = properties_clean['latitude'].mean()
        center_lon = properties_clean['longitude'].mean()

        # Create a Folium map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

        # Add markers for each property
        for idx, row in properties_clean.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                # Clean up permalink for display as address
                address_display = row['permalink'].split('_M')[0].replace('-', ' ').replace('_', ', ').strip()
                popup_text = f"<b>Address:</b> {address_display}<br>" \
                            f"<b>Price:</b> ${row['sold_price']:,}<br>" \
                            f"<b>Beds:</b> {row['beds']}<br>" \
                            f"<b>Baths:</b> {row['full_baths']}<br>" \
                            f"<a href='{row['property_url']}' target='_blank'>View Listing</a>"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_text,
                    tooltip=address_display # Use the cleaned address for tooltip as well
                ).add_to(m)

        # Display the map
        display(m)
    else:
        print("No properties with valid latitude and longitude to plot.")

if __name__ == "__main__":
    main()

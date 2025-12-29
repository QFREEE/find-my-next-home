from homeharvest import scrape_property

def main():
   

    properties = scrape_property(
        location="San Diego, CA",
        listing_type="sold",  # for_sale, for_rent, pending
        past_days=30
    )

    properties.to_csv("results.csv", index=False)
    print(f"Found {len(properties)} properties")


if __name__ == "__main__":
    main()

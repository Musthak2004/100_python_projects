def mile_to_km_converter():
    print("\n" + "=" * 40)
    print("   Mile to KM Converter")
    print("=" * 40)

    try:
        miles = float(input("\nEnter the distance in miles: "))
    except ValueError:
        print("Please enter a valid number.")
        return
    
    if miles < 0:
        print("Distance connot be negative.")
        return
    
    # Conversion factor: 1 mile = 1.609344 kilometers
    km = miles * 1.609344

    # Round to 2 decimal places
    km_rounded = round(km, 2)

    print(f"\nDistance in kilometers: {km_rounded} km")
    print(f"Calculation used: {miles} miles x 1.609344 = {km} km")

    print("\n" + "=" * 40)

if __name__ == "__main__":mile_to_km_converter()
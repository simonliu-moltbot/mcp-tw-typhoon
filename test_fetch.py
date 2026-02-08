if __name__ == "__main__":
    import sys
    sys.path.append('src')
    from logic import fetch_suspension_status, check_city_suspension
    print("Testing fetch...")
    data = fetch_suspension_status()
    print(f"Update time: {data.get('updated_at')}")
    print(f"Cities found: {len(data.get('cities', []))}")
    if data.get('cities'):
        print(f"First city: {data['cities'][0]}")
    
    print("\nChecking '台北'...")
    print(check_city_suspension("台北"))

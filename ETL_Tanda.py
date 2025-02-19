from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape the data from the fetched HTML using BeautifulSoup
def scrape_table_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []

    # Find all date elements (assuming they are in <span> tags)
    dates = [span.text.strip() for span in soup.find_all('span', class_='text-gray-800 font-bold text-xl')]

    # Find all table rows
    rows = soup.find_all('tr')

    date_index = 0  # Initialize a date index to track the current date

    for row in rows:
        # Check if row contains "Planifié" and skip if true
        if row.find('td') and 'Planifié:' in row.find('td').text:
            continue
        
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]

        if len(cols) > 0:
            # Assign date to the row
            if date_index < len(dates):
                date = dates[date_index]  # Get the current date
                date_index += 1  # Move to the next date only after assigning it
            else:
                date = ''  # If no dates left, just add an empty string

            data.append([date] + cols)  # Include date with the row data

    return data

def scrape_weekly_data(page, start_date, end_date):
    all_data = []
    while start_date <= end_date:
        # Navigate to the current week
        page.fill('input[type="date"]', start_date.strftime("%Y-%m-%d"))
        page.press('input[type="date"]', 'Enter')
        page.wait_for_timeout(3000)  # Increased timeout to allow full page load
        
        # Loop through all pages of the current week
        while True:
            # Wait for the content to load
            page.wait_for_selector('#shifts', timeout=30000)
            html = page.inner_html('#shifts')

            # Scrape the data
            table_data = scrape_table_data(html)
            if table_data:
                # Add the current week date to each row
                for row in table_data:
                    row.insert(0, start_date.strftime("%Y-%m-%d"))
                all_data.extend(table_data)

            # Check if there's a next page and navigate
            try:
                next_button = page.locator('button[aria-label="Next"]')
                if next_button.is_disabled(timeout=3000):
                    print("No more pages for the week.")
                    break
                else:
                    next_button.click()
                    page.wait_for_timeout(3000)  # Adjust based on your connection speed
            except Exception as e:
                print(f"Error navigating to the next page: {e}")
                break

        # Move to the next week
        start_date += timedelta(weeks=1)

    return all_data

def main():
    # Get email and password from the user
    email = input("Enter your email: ")
    password = input("Enter your password: ")  # Hide password input

    # Get start date from the user
    start_date_input = input("Enter the start date (DD-MM-YYYY): ")
    start_date = datetime.strptime(start_date_input, "%d-%m-%Y")  # Change format to %d-%m-%Y
    end_date = datetime.now()  # Use today's date as the end date

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()
        page.goto('https://eu.workforce.com/mobile_app/login')
        
        # Log in to the website
        page.get_by_placeholder("Email").fill(email)
        page.get_by_placeholder("Password").fill(password)
        page.get_by_placeholder("Password").press("Enter")
        
        # Wait for the navigation to complete and ensure the target page is loaded
        page.wait_for_load_state('networkidle')
        
        # Navigate to "Feuilles de temps" page
        page.get_by_role("link", name="Feuilles de temps").click()
        page.wait_for_load_state('networkidle')

        # Scrape data week by week
        all_data = scrape_weekly_data(page, start_date, end_date)
        
        # Close the browser
        browser.close()

        # Save the data to a CSV file
        if all_data:
            # Get the maximum number of columns in any row
            max_columns = max(len(row) for row in all_data)
            # Ensure all rows have the same number of columns
            all_data = [row + [''] * (max_columns - len(row)) for row in all_data]
            df = pd.DataFrame(all_data, columns=['Week Date', 'Date'] + [f"Column{i+1}" for i in range(max_columns - 2)])
            df.to_csv('data.csv', index=False)
            print("Data has been successfully scraped and saved to 'data.csv'")
        else:
            print("No table data found.")

if __name__ == "__main__":
    main()

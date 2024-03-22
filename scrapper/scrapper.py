import requests
from bs4 import BeautifulSoup
import csv

# Function to scrape the main events page
def scrape_main_events_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table or list that contains all the events
    events = soup.find_all('a', class_='b-statistics__table-content')
    events_data = []

    for event in events:
        event_name = event.text.strip()
        event_url = event['href']
        event_date_location = event.find_next_sibling('some-element').text.strip() # Replace with actual element
        
        # You can parse event_date_location here to separate the date and location
        # ...

        events_data.append({
            'event_name': event_name,
            'event_url': event_url,
            # 'event_date': event_date,
            # 'event_location': event_location
            'event_date_location': event_date_location
        })
    
    return events_data

# Main function
def main():
    main_url = 'http://www.ufcstats.com/statistics/events/completed'
    events_data = scrape_main_events_page(main_url)
    
    # Save the data to a CSV file
    with open('ufc_events.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['event_name', 'event_url', 'event_date', 'event_location'])
        writer.writeheader()
        writer.writerows(events_data)

if __name__ == "__main__":
    main()

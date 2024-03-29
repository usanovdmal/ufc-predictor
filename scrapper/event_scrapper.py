import requests
from bs4 import BeautifulSoup
import json

def scrape_individual_fight_details(url):
    # Send request and create soup object
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    fight_data = {}

    # Extract the fighters and results
    fighters = soup.select('.b-fight-details__person')
    fight_data['fighters'] = []
    for fighter in fighters:
        name = fighter.select_one('.b-fight-details__person-name a').text.strip()
        result = fighter.select_one('.b-fight-details__person-status').get_text(strip=True)
        fight_data['fighters'].append({'name': name, 'result': result})

    # Get the weight class
    fight_data['weight_class'] = soup.find('i', class_='b-fight-details__fight-title').get_text(strip=True).replace(' Bout', '')

    # Get Method, Round, Time, Time format, Referee, and Judges from the details
    details = soup.select('div.b-fight-details__content > p.b-fight-details__text > i')

    for detail in details:
        label_tag = detail.find('i', class_='b-fight-details__label')
        if label_tag:
            label = label_tag.get_text(strip=True).rstrip(':')
            if label == "Referee":
                # The referee's name is within a span tag following the label
                referee_tag = label_tag.find_next_sibling('span')
                fight_data['referee'] = referee_tag.get_text(strip=True) if referee_tag else ""
            elif label == "Method":
                # The value is within an i tag with style set to normal following the label
                method_tag = label_tag.find_next_sibling('i', style="font-style: normal")
                fight_data['method'] = method_tag.get_text(strip=True) if method_tag else ""
            elif label == "Details":
                fight_data['judges'] = {}
            else:
                value_tag = label_tag.next_sibling
                fight_data[label.lower().replace(' ', '_')] = value_tag.strip() if value_tag else ""

    # Extract Judges scores
    judges_scores = soup.select('i.b-fight-details__text-item:not(:has(.b-fight-details__label))')
    judges_list = []
    for i_tag in judges_scores:
        judge_name = i_tag.find('span').get_text(strip=True)
        score_text = i_tag.get_text(strip=True).replace(judge_name, '').strip().rstrip('.')
        judges_list.append({'name': judge_name, 'score': score_text})
    fight_data['judges'] = judges_list

    # Totals and Significant Strikes
    all_tables = soup.find_all('table')
    for table in all_tables:
        table_title = table.find_previous('p').text.strip()
        if 'Totals' in table_title:
            category = 'totals'
        elif 'Significant Strikes' in table_title:
            category = 'significant_strikes'
        else:
            continue  # If it's not one of the tables we want, skip it

        headers = [th.text.strip() for th in table.find_all('th')]
        rows = table.find_all('tr', class_='b-fight-details__table-row')
        for row in rows:
            cols = row.find_all('td')
            fighter_name = cols[0].find('p').text.strip()
            values = [td.text.strip() for td in cols[1:]]
            fight_data[category][fighter_name] = dict(zip(headers[1:], values))

    # Per Round
    rnd_headers = []
    rnd_tables = soup.find_all('table', class_='b-fight-details__table js-fight-table')
    for table in rnd_tables:
        headers = [th.text.strip() for th in table.find_all('th')][1:]  # skip the 'Fighter' header
        rnd_headers.extend(headers)

        for thead in table.find_all('thead', class_='b-fight-details__table-row_type_head'):
            round_number = thead.th.text.strip()
            rows = thead.find_next_sibling('tbody').find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                fighter_name = cols[0].find('p').text.strip()
                values = [td.text.strip() for td in cols[1:]]
                round_data = dict(zip(rnd_headers, values))
                fight_data['per_round'].append({'round': round_number, fighter_name: round_data})

    return fight_data

# Function to scrape the fight details from an event page
def scrape_fight_details(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all rows with fight details
    fight_rows = soup.find_all('tr', class_='js-fight-details-click')
    fights_data = []

    for fight_row in fight_rows:
        # Extracting the URL from the data-link attribute
        fight_details_url = fight_row['data-link']
        
        # You would then call your scrape_individual_fight_details function here
        individual_fight_data = scrape_individual_fight_details(fight_details_url)
        fights_data.append(individual_fight_data)

    return fights_data

# Function to scrape the main events page and individual fight details
def scrape_main_events_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    events_table = soup.find('table', class_='b-statistics__table-events')
    events_data = []
    event_rows = events_table.find_all('tr', class_='b-statistics__table-row')

    for event_row in event_rows:
        cells = event_row.find_all('td')
        if len(cells) == 2:
            event_detail = cells[0].find('a')
            event_date = cells[0].find('span', class_='b-statistics__date')
            event_location = cells[1].get_text(strip=True)

            if event_detail and event_date:
                event_name = event_detail.text.strip()
                event_url = event_detail['href']
                event_date = event_date.text.strip()

                # Scrape fight details for each event
                fights_data = scrape_fight_details(event_url)

                event_data = {
                    'event_name': event_name,
                    'event_url': event_url,
                    'event_date': event_date,
                    'event_location': event_location,
                    'fights': fights_data  # Store fight details within each event
                }
                events_data.append(event_data)

    return events_data

# Main function
def main():
    main_url = 'http://www.ufcstats.com/statistics/events/completed?page=all'
    events_data = scrape_main_events_page(main_url)

    # Save the data to a JSON file
    with open('ufc_events.json', 'w', encoding='utf-8') as file:
        json.dump(events_data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()

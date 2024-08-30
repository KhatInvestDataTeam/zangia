import os 
import sys 

import re
import requests
from bs4 import BeautifulSoup
import scrapy

import pandas as pd 

def extract_salary_range(salary: str) -> tuple:
    try:
        salary = salary.replace(',', '')
        salary = salary.replace(' ', '')
        parts = salary.split('-')
        
        # Strip whitespace and convert to integers
        low = int(parts[0].strip())
        high = int(parts[1].strip()) if len(parts) > 1 else low
    except:
        salary = salary.replace('Тохиролцоно', '')
        low = int(salary)
        high = 'Тохиролцоно'
        
    
    return low, high

def scrape_page(url: str) -> list:
    data = []

    # Send a GET request to the webpage
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'lxml')

        print('Processing page:', url)
        
        # Find all job listings (div with class 'list')
        job_listings = soup.find_all('div', class_='list')

        for job in job_listings:
            try:
                salary = job.find('span', class_='fsal').text.strip()
                #low, high = extract_salary_range(salary)
                titles = [b_tag.text for b_tag in job.find_all('b')]

                # Ensure there are enough titles
                if len(titles) >= 3:
                    data.append([titles[0], salary, titles[1], titles[2]])
            except Exception as e:
                print(f"Error processing job listing: {e}")

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    return data

def main() -> None:
    base_url = 'https://www.zangia.mn/job/list'
    page = 1
    all_data = []

    for page in range(1, 232):
        url = f'{base_url}/pg.{page}'
        page_data = scrape_page(url)
        
        if not page_data:
            break
        
        all_data.extend(page_data)


    # Save data to Excel
    df = pd.DataFrame(columns=['Title', 'Salary', 'company', 'date'], data=all_data)
    df.to_excel('zangia.xlsx', index=False)

if __name__ == '__main__':
    main()
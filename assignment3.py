#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""IS211 Assignment 3: Web Log Processing

This script downloads a web log file in CSV format, processes it to find
image requests and the most popular browser, and provides statistics on
hits by hour of the day.
"""

import argparse
import csv
import re
import urllib.request
from datetime import datetime
from collections import Counter


def download_data(url):
    """
    Download data from the specified URL and return it as a string.
    
    Args:
        url (str): The URL to download the data from.
        
    Returns:
        str: The downloaded data as a string.
    """
    with urllib.request.urlopen(url) as response:
        data = response.read().decode('utf-8')
    return data


def process_csv(data):
    """
    Process the CSV data and return a list of dictionaries representing each row.
    
    Args:
        data (str): The CSV data as a string.
        
    Returns:
        list: A list of dictionaries containing the processed data.
    """
    processed_data = []
    csv_reader = csv.reader(data.splitlines())
    
    for row in csv_reader:
        if len(row) >= 5:  # Ensure there are enough columns
            log_entry = {
                'path': row[0].strip(),
                'datetime': row[1].strip(),
                'browser': row[2].strip(),
                'status': row[3].strip(),
                'size': row[4].strip()
            }
            processed_data.append(log_entry)
    
    return processed_data


def find_image_requests(data):
    """
    Find all requests for image files (.jpg, .gif, .png) and calculate their percentage.
    
    Args:
        data (list): The processed web log data.
        
    Returns:
        tuple: (image_count, percentage_of_images)
    """
    # Create a regular expression pattern to match image file extensions
    image_regex = re.compile(r'.*\.(jpg|gif|png)$', re.IGNORECASE)
    
    # Count image requests
    image_count = 0
    for entry in data:
        if image_regex.match(entry['path']):
            image_count += 1
    
    # Calculate percentage
    total_requests = len(data)
    if total_requests > 0:
        percentage = (image_count / total_requests) * 100
    else:
        percentage = 0
    
    return image_count, percentage


def find_most_popular_browser(data):
    """
    Find the most popular browser used in the web log data.
    
    Args:
        data (list): The processed web log data.
        
    Returns:
        tuple: (most_popular_browser, count)
    """
    browser_counts = Counter()
    
    # Regular expressions to identify browsers
    firefox_regex = re.compile(r'Firefox/\d+', re.IGNORECASE)
    chrome_regex = re.compile(r'Chrome/\d+', re.IGNORECASE)
    ie_regex = re.compile(r'MSIE \d+|Trident/\d+', re.IGNORECASE)
    safari_regex = re.compile(r'Safari/\d+', re.IGNORECASE)
    
    for entry in data:
        user_agent = entry['browser']
        
        # Check which browser is being used
        if firefox_regex.search(user_agent):
            browser_counts['Firefox'] += 1
        elif chrome_regex.search(user_agent):
            browser_counts['Chrome'] += 1
        elif ie_regex.search(user_agent):
            browser_counts['Internet Explorer'] += 1
        elif safari_regex.search(user_agent) and not chrome_regex.search(user_agent):
            # Safari includes "Safari" in user agent, but Chrome does too, so check Chrome first
            browser_counts['Safari'] += 1
        else:
            browser_counts['Other'] += 1
    
    # Find the most popular browser
    most_popular = browser_counts.most_common(1)
    if most_popular:
        return most_popular[0]  # (browser_name, count)
    else:
        return ('None', 0)


def analyze_hits_by_hour(data):
    """
    Analyze the number of hits by hour of the day.
    
    Args:
        data (list): The processed web log data.
        
    Returns:
        list: A list of tuples (hour, hit_count) sorted by hit_count in descending order.
    """
    hour_counts = Counter()
    
    for entry in data:
        try:
            # Parse datetime string (format: MM/DD/YYYY HH:MM:SS)
            date_obj = datetime.strptime(entry['datetime'], '%m/%d/%Y %H:%M:%S')
            hour = date_obj.hour
            hour_counts[hour] += 1
        except ValueError:
            # Skip entries with invalid datetime format
            continue
    
    # Sort by count in descending order
    return sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)


def main():
    """Main function to run the program."""
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='URL to the weblog CSV file', required=True)
    args = parser.parse_args()
    
    try:
        # Part I: Download the data
        print(f"Downloading data from {args.url}...")
        csv_data = download_data(args.url)
        
        # Part II: Process the CSV data
        print("Processing CSV data...")
        log_entries = process_csv(csv_data)
        print(f"Processed {len(log_entries)} log entries")
        
        # Part III: Find image requests
        print("Analyzing image requests...")
        image_count, image_percentage = find_image_requests(log_entries)
        print(f"Image requests account for {image_percentage:.1f}% of all requests")
        
        # Part IV: Find most popular browser
        print("Determining most popular browser...")
        most_popular_browser, browser_count = find_most_popular_browser(log_entries)
        print(f"The most popular browser is {most_popular_browser} with {browser_count} hits")
        
        # Extra Credit: Analyze hits by hour
        print("\nExtra Credit - Hits by Hour:")
        hits_by_hour = analyze_hits_by_hour(log_entries)
        for hour, count in hits_by_hour:
            print(f"Hour {hour:02d} has {count} hits")
        
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()

from termcolor import colored
import shodan
import threading
import os
import subprocess

# Print title
title = "Shodan IP grabber 2023"
author = "Coded by @O9NEON"
print(colored(title.center(50), 'green'))
print(colored(author.center(50), 'green'))
print()

#check if termcolor module is installed and install if necessary
try:
  import termcolor
except ImportError:
  print("termcolor module not found. Installing...")
  subprocess.check_call(["pip", "install", "termcolor"])
  import termcolor

# Check if shodan module is installed and install if necessary
try:
  import shodan
except ImportError:
  print("shodan module not found. Installing...")
  subprocess.check_call(["pip", "install", "shodan"])
  import shodan

# Check if threading module is installed and install if necessary
try:
  import threading
except ImportError:
  print("threading module not found. Installing...")
  subprocess.check_call(["pip", "install", "threading"])
  import threading

# Check if os module is installed and install if necessary
try:
  import os
except ImportError:
  print("os module not found. Installing...")
  subprocess.check_call(["pip", "install", "os"])
  import os

# Rest of your code goes here

api_key = input("Enter your Shodan API key: ")
api = shodan.Shodan(api_key)


def download_results(start, end, results, filename):
  with open(filename, 'a') as f:
    for i in range(start, end):
      f.write(str(results['matches'][i]) + '\n')


try:
  # Get API info to show balance and credits
  info = api.info()
  print("API key is associated with the %s plan." % info["plan"])
  print("Query credits available: %d" % info["query_credits"])

  # Prompt user for search query
  search_query = input("Enter search query: ")

  # Prompt user for number of results to download
  num_results = int(input("Enter number of results to download: "))

  # Prompt user for output filename
  output_filename = input("Enter output filename: ")

  # Prompt user for number of threads to use
  num_threads = int(input("Enter number of threads to use (MAX 9): "))

  # Perform search and download results
  print("Performing search...")
  results = api.search(search_query, limit=num_results)

  print("Downloading results...")
  threads = []
  total = len(results['matches'])
  chunk_size = total // num_threads  # split the results into num_threads chunks
  for i in range(0, total, chunk_size):
    start = i
    end = min(i + chunk_size, total)
    t = threading.Thread(target=download_results,
                         args=(start, end, results, output_filename))
    threads.append(t)
    t.start()

  # Wait for all threads to complete
  for t in threads:
    t.join()

  print("\nResults saved to %s" % output_filename)

  # Extract IPs to ip.txt if requested
  extract_ips = input("Extract IPs to ip.txt? (y/n): ")
  if extract_ips.lower() == 'y':
    ips = set()
    with open(output_filename, 'r') as f:
      for line in f:
        if '"ip": "' in line:
          ip = line.split('"ip": "')[1].split('"')[0]
          ips.add(ip)
    with open('ip.txt', 'w') as f:
      for ip in ips:
        f.write(ip + '\n')
    print("IPs extracted to ip.txt")

  # Extract hostnames to host.txt if requested
  extract_hosts = input("Extract hostnames to host.txt? (y/n): ")
  if extract_hosts.lower() == 'y':
    hosts = set()
    with open(output_filename, 'r') as f:
      for line in f:
        if '"http": {' in line and '"host": "' in line:
          host = line.split('"http": {')[1].split('"host": "')[1].split('"')[0]
          hosts.add(host)
    with open('host.txt', 'w') as f:
      for host in hosts:
        f.write(host + '\n')
    print("Hostnames extracted to host.txt")

# Auto-generate ip.txt and host.txt if they don't exist
  if not os.path.exists('ip.txt'):
    with open('ip.txt', 'w') as f:
      print("ip.txt created")
  if not os.path.exists('host.txt'):
    with open('host.txt', 'w') as f:
      print("host.txt created")

except shodan.APIError as e:
  print('Error: %s' % e)

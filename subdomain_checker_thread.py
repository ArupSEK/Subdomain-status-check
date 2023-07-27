import argparse
import requests
from colorama import Fore, Style
from art import text2art
from tqdm import tqdm
import concurrent.futures

def install_required_libraries():
    try:
        import colorama
    except ImportError:
        print("Colorama library not found. Attempting to install...")
        import subprocess
        subprocess.check_call(["pip", "install", "colorama"])

    try:
        import tqdm
    except ImportError:
        print("Tqdm library not found. Attempting to install...")
        import subprocess
        subprocess.check_call(["pip", "install", "tqdm"])

    try:
        import art
    except ImportError:
        print("Art library not found. Attempting to install...")
        import subprocess
        subprocess.check_call(["pip", "install", "art"])

    try:
        import requests
    except ImportError:
        print("requests library not found. Attempting to install...")
        import subprocess
        subprocess.check_call(["pip", "install", "requests"])

def check_subdomain(subdomain, protocol):
    url = f"{protocol}://{subdomain}"
    try:
        response = requests.get(url)
        if response.status_code < 300:
            return f"{Fore.GREEN}[2xx - {protocol.upper()}] {url}{Style.RESET_ALL}"
        elif 300 <= response.status_code < 400:
            return f"{Fore.BLUE}[3xx - {protocol.upper()}] {url}{Style.RESET_ALL}"
        elif 400 <= response.status_code < 500:
            return f"{Fore.RED}[4xx - {protocol.upper()}] {url}{Style.RESET_ALL}"
        elif 500 <= response.status_code < 600:
            return f"{Fore.YELLOW}[5xx - {protocol.upper()}] {url}{Style.RESET_ALL}"
    except requests.exceptions.RequestException:
        return f"{Fore.YELLOW}[5xx - {protocol.upper()}] {url} [Failed to connect]{Style.RESET_ALL}"

def save_to_file(filename, subdomains):
    with open(filename, "w") as file:
        file.writelines(subdomains)

def display_welcome_message():
    welcome_art = text2art("Welcome to\nRes4divider")
    print(welcome_art)

def check_subdomains_thread(subdomains):
    active_subdomains_2xx_http = []
    active_subdomains_2xx_https = []
    active_subdomains_3xx_http = []
    active_subdomains_3xx_https = []
    inactive_subdomains_4xx_http = []
    inactive_subdomains_4xx_https = []
    inactive_subdomains_5xx_http = []
    inactive_subdomains_5xx_https = []

    for subdomain in tqdm(subdomains, desc="Checking Subdomains", unit="subdomain"):
        subdomain = subdomain.strip()

        result_http = check_subdomain(subdomain, "http")
        if "[2xx - HTTP]" in result_http:
            active_subdomains_2xx_http.append(result_http)\n
        elif "[3xx - HTTP]" in result_http:
            active_subdomains_3xx_http.append(result_http)\n
        elif "[4xx - HTTP]" in result_http:
            inactive_subdomains_4xx_http.append(result_http)\n
        elif "[5xx - HTTP]" in result_http:
            inactive_subdomains_5xx_http.append(result_http)\n

        result_https = check_subdomain(subdomain, "https")
        if "[2xx - HTTPS]" in result_https:
            active_subdomains_2xx_https.append(result_https)\n
        elif "[3xx - HTTPS]" in result_https:
            active_subdomains_3xx_https.append(result_https)\n
        elif "[4xx - HTTPS]" in result_https:
            inactive_subdomains_4xx_https.append(result_https)\n
        elif "[5xx - HTTPS]" in result_https:
            inactive_subdomains_5xx_https.append(result_https)\n

    return (active_subdomains_2xx_http, active_subdomains_3xx_http,
            active_subdomains_2xx_https, active_subdomains_3xx_https,
            inactive_subdomains_4xx_http, inactive_subdomains_4xx_https,
            inactive_subdomains_5xx_http, inactive_subdomains_5xx_https)

def main():
    parser = argparse.ArgumentParser(description="Check the status of subdomains and save them to separate files.")
    parser.add_argument("-D", "--domain-file", required=True, help="Path to the subdomains text file")
    parser.add_argument("-T", "--threads", type=int, default=1, help="Number of threads for concurrent checking")
    args = parser.parse_args()

    install_required_libraries()

    display_welcome_message()

    with open(args.domain_file, "r") as file:
        subdomain_list = file.readlines()

    # Split subdomains into chunks to be processed by individual threads
    chunk_size = len(subdomain_list) // args.threads
    subdomain_chunks = [subdomain_list[i:i + chunk_size] for i in range(0, len(subdomain_list), chunk_size)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        results = list(executor.map(check_subdomains_thread, subdomain_chunks))

    active_subdomains_2xx_http = [subdomain for sublist in results for subdomain in sublist[0]]
    active_subdomains_3xx_http = [subdomain for sublist in results for subdomain in sublist[1]]
    active_subdomains_2xx_https = [subdomain for sublist in results for subdomain in sublist[2]]
    active_subdomains_3xx_https = [subdomain for sublist in results for subdomain in sublist[3]]
    inactive_subdomains_4xx_http = [subdomain for sublist in results for subdomain in sublist[4]]
    inactive_subdomains_4xx_https = [subdomain for sublist in results for subdomain in sublist[5]]
    inactive_subdomains_5xx_http = [subdomain for sublist in results for subdomain in sublist[6]]
    inactive_subdomains_5xx_https = [subdomain for sublist in results for subdomain in sublist[7]]

    save_to_file("2xx_http.txt", active_subdomains_2xx_http)
    save_to_file("3xx_http.txt", active_subdomains_3xx_http)
    save_to_file("2xx_https.txt", active_subdomains_2xx_https)
    save_to_file("3xx_https.txt", active_subdomains_3xx_https)
    save_to_file("4xx_http.txt", inactive_subdomains_4xx_http)
    save_to_file("4xx_https.txt", inactive_subdomains_4xx_https)
    save_to_file("5xx_http.txt", inactive_subdomains_5xx_http)
    save_to_file("5xx_https.txt", inactive_subdomains_5xx_https)

    print("Results saved to files in the current directory.")

if __name__ == "__main__":
    main()

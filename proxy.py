import requests
import time
import urllib.parse
import json
import random

BASE_URL = "https://adsevm.saifpowersoft.top/api/"

def read_queries():
    try:
        with open('query.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and line.startswith('user=')]
    except FileNotFoundError:
        print("query.txt not found.")
        return []

def parse_user_id(init_data):
    try:
        user_str = urllib.parse.unquote(init_data.split('&')[0][5:])
        user_data = json.loads(user_str)
        return user_data['id']
    except Exception as e:
        print(f"Error parsing user_id: {str(e)}")
        return None

def read_useragents(filename="brs.txt"):
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return ['Mozilla/5.0 (Windows NT 10.0; Win64; x64)']

def read_proxies(filename="proxy.txt"):
    try:
        with open(filename, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
            if not proxies:
                return [None]  # fallback to no proxy
            return proxies
    except FileNotFoundError:
        return [None]  # no proxy if file not found

def make_request(endpoint, data=None, useragent=None, proxy=None):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': useragent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    url = f'{BASE_URL}{endpoint}'
    proxies = {"http": proxy, "https": proxy} if proxy else None
    try:
        response = requests.post(url, headers=headers, json=data, proxies=proxies, timeout=15)
        return response
    except Exception as e:
        print(f"Request error: {e}")
        return None

def daily_checkin(init_data, useragent, proxy=None):
    user_id = parse_user_id(init_data)
    payload = {"user_id": user_id, "init_data": init_data}
    try:
        proxies = {"http": proxy, "https": proxy} if proxy else None
        res = requests.post(
            "https://adsevm.saifpowersoft.top/cards.php?action=do_checkin",
            headers={"User-Agent": useragent, "Content-Type": "application/json"},
            data=json.dumps(payload),
            proxies=proxies,
            timeout=15
        )
        data = res.json()
        if data.get("status") == "success":
            print(f"[{user_id}] ✅ Check-in success! Streak: {data.get('streak')} | Reward: {data.get('reward')}")
        else:
            print(f"[{user_id}] ❌ Check-in failed: {data.get('message')}")
    except Exception as e:
        print(f"[{user_id}] ❌ Check-in error: {e}")

def claim_ads(init_data, useragent, proxy=None):
    user_id = parse_user_id(init_data)
    payload = {'user_id': user_id, 'init_data': init_data, 'network': 'gigapub'}

    print(f"\n--- Starting ad claims for user {user_id} ---")

    while True:
        ua = useragent
        watch_time = random.randint(10, 30)
        print(f"[{user_id}] Watching ad for {watch_time}s...")
        time.sleep(watch_time)

        response = make_request('watched.php', payload, useragent=ua, proxy=proxy)

        if not response:
            print(f"[{user_id}] Request failed, skipping...")
            break

        if response.status_code != 200:
            print(f"[{user_id}] Request failed: {response.status_code} - {response.text}")
            break

        try:
            result = response.json()
        except Exception as e:
            print(f"[{user_id}] Error parsing JSON: {e}")
            break

        print(json.dumps(result, indent=2))

        if not result.get("ok", True):
            print(f"[{user_id}] ⛔ Server returned failure or deadlock, retrying after 5s...")
            time.sleep(5)
            continue

        hourly = int(result.get("ads_watched_hourly", 0))
        limit = int(result.get("hourly_limit", 0))

        if hourly >= limit:
            print(f"[{user_id}] ⚠️ Hourly limit reached: {hourly}/{limit}")
            break

        delay = random.randint(5, 15)
        print(f"[{user_id}] Waiting {delay}s before next ad...")
        time.sleep(delay)

if __name__ == "__main__":
    users = read_queries()
    useragents = read_useragents()
    proxies = read_proxies()

    if not users:
        print("No accounts found in query.txt")
        exit(0)

    if not useragents:
        print("No user-agents found in brs.txt")
        exit(0)

    for init_data in users:
        ua = random.choice(useragents)
        proxy = random.choice(proxies)
        user_id = parse_user_id(init_data)
        print(f"\n=== Starting workflow for user {user_id} ===")
        print(f"Using User-Agent: {ua[:60]}...")
        if proxy:
            print(f"Using Proxy: {proxy}")
        else:
            print("Using Proxy: None")

        # Step 1: Daily check-in
        daily_checkin(init_data, ua, proxy)

        # Step 2: Claim ads until hourly limit reached
        claim_ads(init_data, ua, proxy)

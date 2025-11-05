import requests
import time
import os
import json
import urllib.parse
import random
import threading
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class XCXWalletBot:
    def __init__(self):
        self.url = "https://app.xcxwallet.com/api/add_hourly_reward.php"
        self.accounts = self.load_accounts()
        self.mode = self.select_mode()
        self.lock = threading.Lock()

        # Daftar User-Agent yang realistic
        self.user_agents = [
            # Windows - Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",

            # Windows - Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",

            # macOS - Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",

            # macOS - Chrome
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

            # Linux - Firefox
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",

            # Mobile - iOS
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",

            # Mobile - Android
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36"
        ]

        if not self.accounts:
            raise ValueError("Tidak ada akun yang ditemukan")

    def select_mode(self):
        print("\n" + "="*50)
        print("🤖 PILIH MODE CLAIM")
        print("="*50)
        print("1. Normal Mode - Claim setiap 1 jam 1 menit")
        print("2. Fast Mode - Claim setiap 3 detik dengan Multi-Thread")
        print("3. Stealth Mode - Claim dengan delay acak dan rotasi User-Agent")

        while True:
            try:
                choice = input("\nPilih mode (1-3): ").strip()
                if choice == "1":
                    return "normal"
                elif choice == "2":
                    return "fast"
                elif choice == "3":
                    return "stealth"
                else:
                    print("Pilihan tidak valid. Silakan pilih 1, 2 atau 3.")
            except KeyboardInterrupt:
                print("\nBot dihentikan")
                exit()

    def load_accounts(self):
        accounts = []
        env_vars = dict(os.environ)

        for key, value in env_vars.items():
            if key.startswith('INIT_DATA_'):
                account_name = key.replace('INIT_DATA_', '')
                accounts.append({
                    'name': account_name,
                    'init_data': value,
                    'user_id': self.parse_user_id(value),
                    'status': 'Waiting first claim',
                    'last_claim': 'Never',
                    'success_count': 0,
                    'fail_count': 0,
                    'consecutive_fails': 0  # Track gagal berturut-turut
                })
                print(f"✅ {account_name} loaded")

        print(f"\n📊 Total {len(accounts)} accounts ready")
        return accounts

    def parse_user_id(self, init_data):
        try:
            decoded = urllib.parse.unquote(init_data)
            user_start = decoded.find('"id":') + 5
            user_end = decoded.find(',', user_start)
            return decoded[user_start:user_end].strip()
        except:
            return "unknown"

    def get_random_headers(self):
        """Generate headers yang realistic dengan User-Agent acak"""
        user_agent = random.choice(self.user_agents)

        # Deteksi browser dari User-Agent untuk headers yang konsisten
        if "Chrome" in user_agent:
            sec_ch_ua = '"Chromium";v="120", "Google Chrome";v="120", "Not=A?Brand";v="99"'
            sec_ch_ua_platform = '"Windows"'
        elif "Firefox" in user_agent:
            sec_ch_ua = '"Not/A)Brand";v="99", "Firefox";v="121"'
            sec_ch_ua_platform = '"Windows"'
        elif "Safari" in user_agent:
            sec_ch_ua = '"Safari";v="17", "Apple";v="15"'
            sec_ch_ua_platform = '"macOS"'
        else:
            sec_ch_ua = '"Not/A)Brand";v="99"'
            sec_ch_ua_platform = '"Linux"'

        return {
            'authority': 'app.xcxwallet.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,id;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://app.xcxwallet.com',
            'referer': 'https://app.xcxwallet.com/index.php',
            'sec-ch-ua': sec_ch_ua,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': sec_ch_ua_platform,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': user_agent,
        }

    def claim_reward(self, account):
        payload = {
            "user_id": int(account['user_id']) if account['user_id'].isdigit() else 0,
            "reward": 0.04,
            "init_data": account['init_data']
        }

        try:
            # Gunakan session untuk koneksi yang lebih baik
            with requests.Session() as session:
                session.headers.update(self.get_random_headers())

                # Tambahkan delay acak sebelum request
                delay_before = random.uniform(0.5, 2.0)
                time.sleep(delay_before)

                response = session.post(
                    self.url,
                    json=payload,
                    timeout=30,
                    allow_redirects=True
                )

            if response.status_code == 200:
                result = response.json()

                if result.get('ok'):
                    with self.lock:
                        account['status'] = 'Claimed'
                        account['last_claim'] = datetime.now().strftime('%H:%M:%S')
                        account['success_count'] += 1
                        account['consecutive_fails'] = 0  # Reset consecutive fails
                    return True, result.get('message', 'Success')
                else:
                    error_msg = result.get('message', '').lower()
                    if 'already' in error_msg or 'wait' in error_msg:
                        with self.lock:
                            account['status'] = 'Already claimed'
                            account['last_claim'] = datetime.now().strftime('%H:%M:%S')
                            account['consecutive_fails'] = 0
                        return True, 'Already claimed'
                    else:
                        with self.lock:
                            account['status'] = 'Failed'
                            account['fail_count'] += 1
                            account['consecutive_fails'] += 1
                        return False, result.get('message', 'Unknown error')
            else:
                with self.lock:
                    account['status'] = f'HTTP Error {response.status_code}'
                    account['fail_count'] += 1
                    account['consecutive_fails'] += 1
                return False, f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            with self.lock:
                account['status'] = 'Timeout'
                account['fail_count'] += 1
                account['consecutive_fails'] += 1
            return False, "Request timeout"
        except requests.exceptions.ConnectionError:
            with self.lock:
                account['status'] = 'Connection Error'
                account['fail_count'] += 1
                account['consecutive_fails'] += 1
            return False, "Connection error"
        except Exception as e:
            with self.lock:
                account['status'] = 'Error'
                account['fail_count'] += 1
                account['consecutive_fails'] += 1
            return False, str(e)

    def claim_account_thread(self, account, results):
        success, message = self.claim_reward(account)
        results.append((account['name'], success, message))

    def display_status(self):
        print(f"\n{datetime.now().strftime('%H:%M:%S')} - Status:")
        print("=" * 70)

        total_success = 0
        total_fail = 0
        active_accounts = 0

        for account in self.accounts:
            if account['consecutive_fails'] >= 3:
                status_icon = "🚫"  # Account suspended/blocked
            elif account['status'] == 'Claimed':
                status_icon = "✅"
            elif account['status'] == 'Already claimed':
                status_icon = "⏭️"
            else:
                status_icon = "❌"
                active_accounts += 1

            print(f"{status_icon} {account['name']:12} | {account['status']:20} | Last: {account['last_claim']:8} | ✅{account['success_count']:2} | ❌{account['fail_count']:2}")
            total_success += account['success_count']
            total_fail += account['fail_count']

        print("=" * 70)
        print(f"TOTAL: ✅{total_success} | ❌{total_fail} | Active: {active_accounts}/{len(self.accounts)}")

    def run_normal_mode(self):
        print("\n" + "="*50)
        print("MODE NORMAL - Claim setiap 1 jam 1 menit")
        print("="*50)

        cycle = 0

        try:
            while True:
                cycle += 1
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n🔄 CYCLE #{cycle} - {current_time}")

                # Acak urutan akun setiap cycle
                random.shuffle(self.accounts)

                for account in self.accounts:
                    # Skip akun yang sudah 3x gagal berturut-turut
                    if account['consecutive_fails'] >= 3:
                        print(f"🚫 Skipping {account['name']} (suspected blocked)")
                        continue

                    print(f"Processing {account['name']}...", end=" ")

                    success, message = self.claim_reward(account)

                    if success:
                        if 'already' in message.lower():
                            print("⏭️ Already claimed")
                        else:
                            print("✅ Claimed")
                    else:
                        print(f"❌ Failed: {message}")

                    # Delay acak antara akun
                    delay = random.uniform(2, 5)
                    time.sleep(delay)

                self.display_status()

                wait_time = 3660  # 1 jam 1 menit
                print(f"\n⏰ Next cycle in {wait_time//60} minutes...")

                # Progress bar dengan update setiap 30 detik
                for i in range(wait_time, 0, -30):
                    mins = i // 60
                    secs = i % 60
                    if mins > 0:
                        print(f"⏳ {mins:2d} minutes {secs:2d} seconds remaining...", end='\r')
                    else:
                        print(f"⏳ {secs:2d} seconds remaining...", end='\r')
                    time.sleep(30)

        except KeyboardInterrupt:
            print(f"\n\n🛑 Bot dihentikan oleh user")
            self.display_status()

    def run_fast_mode(self):
        print("\n" + "="*50)
        print("FAST MODE - Claim setiap 3 detik dengan Multi-Thread")
        print("="*50)
        print("⚠️  WARNING: Mode ini sangat mengerikan nyooo!")

        cycle = 0

        try:
            while True:
                cycle += 1
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n⚡ BATCH #{cycle} - {current_time}")

                threads = []
                results = []

                # Filter akun yang tidak blocked
                active_accounts = [acc for acc in self.accounts if acc['consecutive_fails'] < 3]

                for account in active_accounts:
                    thread = threading.Thread(
                        target=self.claim_account_thread,
                        args=(account, results)
                    )
                    threads.append(thread)
                    thread.start()

                for thread in threads:
                    thread.join()

                for name, success, message in results:
                    if success:
                        if 'already' in message.lower():
                            print(f"⏭️ {name}: Already claimed")
                        else:
                            print(f"✅ {name}: Claimed")
                    else:
                        print(f"❌ {name}: Failed - {message}")

                self.display_status()

                print(f"\n⏰ Next batch in 3 seconds...")
                for i in range(1, 0, -1):
                    print(f"⏳ {i} seconds remaining...", end='\r')
                    time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n\n🛑 Bot dihentikan oleh user")
            self.display_status()

    def run_stealth_mode(self):
        print("\n" + "="*50)
        print("STEALTH MODE - Claim dengan delay acak dan rotasi User-Agent")
        print("="*50)
        print("🎭 Mode stealth diaktifkan - Sulit terdeteksi sebagai bot")

        cycle = 0

        try:
            while True:
                cycle += 1
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n🕵️ STEALTH CYCLE #{cycle} - {current_time}")

                # Acak urutan akun
                random.shuffle(self.accounts)

                for account in self.accounts:
                    # Skip akun yang sudah 3x gagal berturut-turut
                    if account['consecutive_fails'] >= 3:
                        print(f"🚫 Skipping {account['name']} (suspected blocked)")
                        continue

                    print(f"🕵️ Processing {account['name']}...", end=" ")

                    success, message = self.claim_reward(account)

                    if success:
                        if 'already' in message.lower():
                            print("⏭️ Already claimed")
                        else:
                            print("✅ Claimed")
                    else:
                        print(f"❌ Failed: {message}")

                    # Delay acak yang lebih panjang dan tidak terprediksi
                    delay = random.uniform(10, 30)  # 10-30 detik antara akun
                    print(f"💤 Waiting {delay:.1f}s...", end="\r")
                    time.sleep(delay)

                self.display_status()

                # Wait time acak antara 55-65 menit (tidak tepat 1 jam)
                wait_time = random.randint(3300, 3900)  # 55-65 menit
                minutes = wait_time // 60
                print(f"\n⏰ Next stealth cycle in ~{minutes} minutes...")

                # Progress dengan interval acak
                remaining = wait_time
                while remaining > 0:
                    interval = random.randint(45, 75)  # Interval acak
                    if interval > remaining:
                        interval = remaining

                    mins = remaining // 60
                    secs = remaining % 60
                    if mins > 0:
                        print(f"⏳ ~{mins:2d}m {secs:2d}s remaining...", end='\r')
                    else:
                        print(f"⏳ {secs:2d}s remaining...", end='\r')

                    time.sleep(interval)
                    remaining -= interval

        except KeyboardInterrupt:
            print(f"\n\n🛑 Bot dihentikan oleh user")
            self.display_status()

    def run(self):
        if self.mode == "normal":
            self.run_normal_mode()
        elif self.mode == "fast":
            self.run_fast_mode()
        else:
            self.run_stealth_mode()

if __name__ == "__main__":
    try:
        bot = XCXWalletBot()
        bot.run()
    except Exception as e:
        print(f"❌ Error: {str(e)}")

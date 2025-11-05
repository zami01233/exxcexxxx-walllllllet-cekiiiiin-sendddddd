import os
import requests
import time
import json
from urllib.parse import parse_qs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class XCXWalletBot:
    def __init__(self):
        self.api_url = "https://app.xcxwallet.com/api/send_wallet.php"
        self.accounts = self.load_accounts()

    def load_accounts(self):
        """Load semua akun dari environment variables"""
        accounts = []
        i = 1
        while True:
            init_data = os.getenv(f'INIT_DATA_ACCOUNT{i}')
            if not init_data:
                break
            accounts.append({
                'number': i,
                'init_data': init_data,
                'user_id': self.extract_user_id(init_data)
            })
            i += 1
        return accounts

    def extract_user_id(self, init_data):
        """Extract user_id dari init_data"""
        try:
            parsed = parse_qs(init_data)
            user_data = parsed.get('user', [None])[0]
            if user_data:
                user_json = json.loads(user_data)
                return user_json.get('id')
        except:
            pass
        return None

    def display_accounts(self):
        """Tampilkan daftar akun yang tersedia"""
        if not self.accounts:
            print("❌ Tidak ada akun yang ditemukan di file .env")
            print("   Pastikan sudah menambahkan INIT_DATA_ACCOUNT1, INIT_DATA_ACCOUNT2, dst.")
            return False

        print("\n" + "="*50)
        print("📋 DAFTAR AKUN TERSEDIA")
        print("="*50)
        for acc in self.accounts:
            print(f"  {acc['number']}. User ID: {acc['user_id']}")
        print("="*50 + "\n")
        return True

    def select_account(self):
        """Pilih akun yang akan digunakan"""
        while True:
            try:
                choice = int(input(f"Pilih akun (1-{len(self.accounts)}): "))
                if 1 <= choice <= len(self.accounts):
                    return self.accounts[choice - 1]
                print(f"❌ Pilih nomor antara 1-{len(self.accounts)}")
            except ValueError:
                print("❌ Input harus berupa angka")

    def send_transaction_method1(self, account, to_address, amount):
        """Method 1: JSON payload dengan Content-Type: application/json"""
        payload = {
            'user_id': account['user_id'],
            'init_data': account['init_data'],
            'to_address': to_address,
            'amount': amount
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://app.xcxwallet.com',
            'Referer': 'https://app.xcxwallet.com/'
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,  # Kirim sebagai JSON
                headers=headers,
                timeout=30
            )

            try:
                response_json = response.json()
                return response.status_code, response_json
            except:
                return response.status_code, response.text

        except Exception as e:
            return 0, str(e)

    def send_transaction_method2(self, account, to_address, amount):
        """Method 2: Form data dengan Content-Type: application/x-www-form-urlencoded"""
        payload = {
            'user_id': str(account['user_id']),
            'init_data': account['init_data'],
            'to_address': to_address,
            'amount': str(amount)
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://app.xcxwallet.com',
            'Referer': 'https://app.xcxwallet.com/'
        }

        try:
            response = requests.post(
                self.api_url,
                data=payload,  # Kirim sebagai form data
                headers=headers,
                timeout=30
            )

            try:
                response_json = response.json()
                return response.status_code, response_json
            except:
                return response.status_code, response.text

        except Exception as e:
            return 0, str(e)

    def send_transaction_method3(self, account, to_address, amount):
        """Method 3: Multipart form-data"""
        payload = {
            'user_id': (None, str(account['user_id'])),
            'init_data': (None, account['init_data']),
            'to_address': (None, to_address),
            'amount': (None, str(amount))
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://app.xcxwallet.com',
            'Referer': 'https://app.xcxwallet.com/'
        }

        try:
            response = requests.post(
                self.api_url,
                files=payload,  # Kirim sebagai multipart
                headers=headers,
                timeout=30
            )

            try:
                response_json = response.json()
                return response.status_code, response_json
            except:
                return response.status_code, response.text

        except Exception as e:
            return 0, str(e)

    def test_all_methods(self, account, to_address, amount):
        """Test semua method untuk menemukan yang benar"""
        print("\n" + "="*50)
        print("🧪 TESTING SEMUA METHOD")
        print("="*50)

        methods = [
            ("Method 1: JSON (application/json)", self.send_transaction_method1),
            ("Method 2: Form Data (x-www-form-urlencoded)", self.send_transaction_method2),
            ("Method 3: Multipart Form Data", self.send_transaction_method3)
        ]

        working_method = None

        for method_name, method_func in methods:
            print(f"\n🔍 Testing {method_name}...")
            status_code, response = method_func(account, to_address, amount)

            print(f"   Status Code: {status_code}")
            if isinstance(response, dict):
                print(f"   Response: {json.dumps(response, indent=6)}")
                if response.get('success'):
                    print(f"   ✅ SUCCESS! Method ini berhasil!")
                    working_method = method_func
                    break
            else:
                print(f"   Response: {response[:200]}")

            time.sleep(1)  # Delay antar test

        return working_method

    def run(self):
        """Jalankan bot"""
        print("\n" + "="*50)
        print("🤖 XCX WALLET AUTO SEND BOT")
        print("="*50)

        # Tampilkan dan pilih akun
        if not self.display_accounts():
            return

        account = self.select_account()
        print(f"\n✅ Akun dipilih: User ID {account['user_id']}\n")

        # Input alamat tujuan
        to_address = input("📤 Masukkan alamat tujuan: ").strip()
        if not to_address:
            print("❌ Alamat tujuan tidak boleh kosong!")
            return

        # Input amount dengan validasi
        while True:
            try:
                amount = int(input("💰 Masukkan jumlah XCX (max 100): "))
                if amount <= 0:
                    print("❌ Jumlah harus lebih dari 0!")
                    continue
                if amount > 100:
                    print("❌ Jumlah maksimal adalah 100 XCX!")
                    continue
                break
            except ValueError:
                print("❌ Input harus berupa angka!")

        # Input jumlah pengulangan
        while True:
            try:
                repeat = int(input("🔄 Berapa kali transaksi? "))
                if repeat <= 0:
                    print("❌ Jumlah pengulangan harus lebih dari 0!")
                    continue
                break
            except ValueError:
                print("❌ Input harus berupa angka!")

        # Test semua method untuk menemukan yang benar
        working_method = self.test_all_methods(account, to_address, amount)

        if not working_method:
            print("\n❌ Tidak ada method yang berhasil!")
            print("💡 Kemungkinan:")
            print("   1. API memerlukan authentication tambahan")
            print("   2. Init data sudah expired")
            print("   3. IP address diblokir")
            print("   4. Saldo tidak mencukupi")
            return

        print("\n" + "="*50)
        print("📊 KONFIRMASI TRANSAKSI")
        print("="*50)
        print(f"  Akun        : User ID {account['user_id']}")
        print(f"  Tujuan      : {to_address}")
        print(f"  Jumlah      : {amount} XCX")
        print(f"  Pengulangan : {repeat}x")
        print(f"  Total       : {amount * repeat} XCX")
        print(f"  Fee/tx      : 2 XCX")
        print(f"  Diterima/tx : {amount - 2} XCX")
        print("="*50)

        confirm = input("\n⚠️  Lanjutkan transaksi? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Transaksi dibatalkan!")
            return

        # Proses transaksi
        print("\n" + "="*50)
        print("🚀 MEMULAI TRANSAKSI")
        print("="*50 + "\n")

        success_count = 0
        failed_count = 0

        for i in range(1, repeat + 1):
            print(f"[{i}/{repeat}] Mengirim {amount} XCX...", end=" ")

            status_code, response = working_method(account, to_address, amount)

            if isinstance(response, dict) and response.get('success'):
                print(f"✅ Berhasil - {response.get('message', '')}")
                success_count += 1
            else:
                msg = response.get('message', str(response)) if isinstance(response, dict) else str(response)
                print(f"❌ Gagal: {msg[:50]}")
                failed_count += 1

            # Delay antar transaksi (kecuali transaksi terakhir)
            if i < repeat:
                time.sleep(2)

        # Summary
        print("\n" + "="*50)
        print("📈 RINGKASAN TRANSAKSI")
        print("="*50)
        print(f"  ✅ Berhasil : {success_count}")
        print(f"  ❌ Gagal    : {failed_count}")
        print(f"  📊 Total    : {repeat}")
        if success_count > 0:
            print(f"  💰 Terkirim : {success_count * amount} XCX")
            print(f"  💸 Fee      : {success_count * 2} XCX")
            print(f"  📥 Diterima : {success_count * (amount - 2)} XCX")
        print("="*50 + "\n")

if __name__ == "__main__":
    bot = XCXWalletBot()
    bot.run()

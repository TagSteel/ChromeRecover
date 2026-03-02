# ChromeRecover

[![GitHub Release](https://img.shields.io/github/v/release/TagSteel/ChromeRecover?display_name=release)](https://github.com/TagSteel/ChromeRecover/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)](https://github.com/TagSteel/ChromeRecover)

**Decrypt and recover saved passwords from Chrome/Chromium encrypted storage**

A cross-platform tool to recover your saved credentials from Chrome's encrypted storage on Windows and Linux.

---

## Features

- ✅ **Windows Support**: Uses DPAPI to decrypt passwords
- ✅ **Linux Support**: AES-GCM decryption with master key extraction
- ✅ **Handles v10/v20 encryption formats**
- ✅ **App-Bound Encryption bypass guide** (Windows)

---

## Prerequisites

### Windows
- Python 3.7+
- `pywin32` module

### Linux
- Python 3.7+
- `pycryptodome` module
- `python-dotenv` module

---

## Installation

```bash
# Clone the repository
git clone https://github.com/TagSteel/ChromeRecover.git
cd ChromeRecover

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Windows

1. Copy your Chrome `Login Data` file to the project directory:
   ```
   %LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data
   ```

2. Run the decryptor:
   ```bash
   python decryptor_windows_final.py
   ```

3. Find decrypted passwords in `decryptedPasswords_Windows.txt`

**Note**: If Chrome uses App-Bound Encryption, follow the [DISABLE_GUIDE.md](DISABLE_GUIDE.md)

### Linux

1. Copy your Chrome `Login Data` file to the project directory:
   ```
   ~/.config/google-chrome/Default/Login Data
   ```

2. Extract your master key and add it to a `.env` file:
   ```bash
   MASTER_KEY_HEX=your_master_key_here
   ```

3. Run the decryptor:
   ```bash
   python decryptor_linux_final.py
   ```

4. Find decrypted passwords in `decryptedPasswords.txt`

---

## Project Structure

```
├── decryptor_windows_final.py       # Windows decryption tool
├── decryptor_linux_final.py         # Linux decryption tool
├── disable_app_bound_encryption.ps1 # PowerShell script for Windows
├── DISABLE_GUIDE.md                 # App-Bound Encryption bypass guide
└── get_key_windows.py               # Key extraction utility
```

---

## Legal Notice

⚠️ **This tool is for educational and personal use only.**

- Only use on **your own Chrome profile**
- Unauthorized access to others' credentials is **illegal**
- The author is not responsible for misuse

Use responsibly and ethically.

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

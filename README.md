# 📧 Email Recon Discord Bot

A powerful Discord bot that performs **email reconnaissance** by checking where an email address is registered — including social media and other platforms — and sends the results to the user's DM.

> ✅ Use responsibly — this tool is intended for educational and security research purposes only.

---

## 🚀 Features

- 🔍 **Recon Command**: `/recon email@example.com` — checks which platforms the email is linked to.
- 📥 **DM Results**: Sends findings privately to the user.
- 🛑 **Anti-abuse**: 10-second cooldown between queries.
- ❌ **Disposable email check**: Blocks temporary/throwaway emails.
- 📡 **MX record validation**: Verifies if the domain has working mail servers.
- 📄 **Help Command**: `/help` for instructions.

---

## 📦 Requirements

- Python 3.8+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### `requirements.txt` should include:
```txt
discord.py
python-dotenv
email-validator
dnspython
```

---

## 🛠️ Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Prthiv/Email-osint.git
   cd Email-osint
   ```

2. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**

   Create a `.env` file in the root folder and add:
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   ```

4. **Run the Bot**
   ```bash
   python bot.py
   ```

---

## ✨ Usage

In your Discord server:

### Recon Command
```bash
/recon example@example.com
```
The bot will verify the email and send results directly to your DMs.

### Help Command
```bash
/help
```
Explains how to use the bot and provides important notes.

---

## ⚠️ Disclaimer

This tool is developed strictly for **educational** and **ethical** purposes. Unauthorized use on emails you do not own or have permission to analyze may be illegal. Use at your own risk.

---

## 🤝 Contributing

Open to contributions and improvements. Feel free to submit a pull request!

---

## 📄 License

MIT License — free to use, modify, and distribute with credit.

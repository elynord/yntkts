import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import subprocess
from cryptography.fernet import Fernet
import base64
import os
import logging
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))

# Logging Configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO  
)

# Replace with your bot token
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Available commands
COMMANDS = {
    "/start": "Start the bot",
    "/help": "Get help",
    "/check": "Check a shell script",
    "/setup": "Install dependencies and run the bot (admin only)",
    "/examples": "Get example shell scripts",
    "/resources": "Get helpful resources for shell scripting",
    "/status": "Get system status (ping, uptime, etc.)",
    "/encrypt_shell": "Encrypt a shell script",
    "/decrypt_shell": "Decrypt a shell script",
    "/menu_lainnya": "Access additional features"
}

# Example scripts and resources
EXAMPLES = {
    "Basic Script": """
#!/bin/bash
echo "Hello, World!"
    """,
    "File Handling": """
#!/bin/bash
filename="$1"
if [ -f "$filename" ]; then
    echo "File exists."
else
    echo "File does not exist."
fi
    """
}

RESOURCES = [
    "ShellCheck: https://www.shellcheck.net/",
    "Bash Guide: https://www.gnu.org/software/bash/manual/",
    "Learn Shell: https://www.learnshell.org/"
]

def start(update, context):
    keyboard = [[telegram.KeyboardButton(command)] for command in COMMANDS]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard)

    update.message.reply_text(
        "👋 Welcome to the Shell Script Checker Bot!\n\n"
        "Please select a command:",
        reply_markup=reply_markup
    )

def help(update, context):
    help_text = "\n".join([f"{command} - {description}" for command, description in COMMANDS.items()])
    update.message.reply_text(f"Here are the available commands:\n\n{help_text}")

def generate_key():
    return Fernet.generate_key()

def encrypt_shell(update, context):
    if update.message.chat.type != "private":
        update.message.reply_text("⚠️ Mohon kirimkan skrip shell Anda secara pribadi ke bot ini.")
        return

    if not update.message.document.file_name.endswith('.sh'):
        update.message.reply_text("❌ Bot hanya bisa mengenkrip file yang berakhiran .sh")
        return

    user_id = update.message.from_user.id
    file_id = update.message.document.file_id
    file_name = f"{user_id}_{update.message.document.file_name}"

    try:
        file = context.bot.getFile(file_id)
        file.download(file_name)

        key = generate_key()
        f = Fernet(key)
        with open(file_name, "rb") as file:
            original = file.read()
        encrypted = f.encrypt(original)

        with open(f"encrypted_{file_name}", "wb") as file:
            file.write(encrypted)

        with open(f"encrypted_{file_name}", "rb") as file:
            context.bot.send_document(chat_id=update.message.chat_id, document=file, filename=f"encrypted_{file_name}")

        key_str = base64.urlsafe_b64encode(key).decode()
        update.message.reply_text(f"✅ Skrip berhasil dienkripsi!\n\nSimpan kunci ini dengan aman:\n\n`{key_str}`", parse_mode=telegram.ParseMode.MARKDOWN)
    except Exception as e:
        update.message.reply_text(f"❌ Terjadi kesalahan saat mengenkripsi: {e}")
    finally:
        os.remove(file_name)
        os.remove(f"encrypted_{file_name}")

def decrypt_shell(update, context):
    if update.message.chat.type != "private":
        update.message.reply_text("⚠️ Mohon kirimkan skrip shell yang dienkripsi secara pribadi ke bot ini.")
        return

    if not update.message.document.file_name.startswith('encrypted_') or not update.message.document.file_name.endswith('.sh'):
        update.message.reply_text("❌ Bot hanya bisa mendekrip file yang berakhiran .sh dan diawali dengan 'encrypted_'")
        return
    
    user_id = update.message.from_user.id
    file_id = update.message.document.file_id
    file_name = f"{user_id}_{update.message.document.file_name}"
    
    # Ask for encryption key
    context.bot.send_message(chat_id=update.message.chat_id, text="🔑 Masukkan kunci enkripsi:")
    
    def process_key(update, context):
        try:
            key_str = update.message.text
            key = base64.urlsafe_b64decode(key_str)
            f = Fernet(key)

            try:
                file = context.bot.getFile(file_id)
                file.download(file_name)
                with open(file_name, "rb") as file:
                    encrypted = file.read()
                decrypted = f.decrypt(encrypted)

                with open(f"decrypted_{file_name[9:]}", "wb") as file: #remove prefix 'encrypted_'
                    file.write(decrypted)
                
                with open(f"decrypted_{file_name[9:]}", "rb") as file:
                    context.bot.send_document(chat_id=update.message.chat_id, document=file, filename=f"decrypted_{file_name[9:]}")

                update.message.reply_text("✅ Skrip berhasil didekripsi!")
            except Exception as e:
                update.message.reply_text(f"❌ Terjadi kesalahan saat mendekripsi: {e}")
            finally:
                os.remove(file_name)
                os.remove(f"decrypted_{file_name[9:]}")

        except Exception as e:
            update.message.reply_text(f"❌ Kunci enkripsi tidak valid: {e}")

def setup(update, context):
    user = update.message.from_user
    if user.id == ADMIN_USER_ID:
        try:
            process = subprocess.Popen(["./install_dependencies.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                message = "✅ Setup completed successfully!"

        except subprocess.CalledProcessError as e:
            message = f"❌ An error occurred during setup: {e.stderr}"
        except Exception as e:
            message = f"❌ An unexpected error occurred: {e}"
    else:
        message = "❌ You are not authorized to run this command."

    context.bot.send_message(chat_id=update.message.chat_id, text=message)

def handle_shell_script(update, context):
    if update.message.chat.type != "private":  # Check if message is in a group
        update.message.reply_text("⚠️ Mohon kirimkan skrip shell Anda secara pribadi ke bot ini.")
        return
    
    if not update.message.document.file_name.endswith('.sh'):
        update.message.reply_text("❌ Bot hanya bisa memeriksa file yang berakhiran .sh")
        return
    user_id = update.message.from_user.id
    file_id = update.message.document.file_id
    file_name = f"{user_id}_{update.message.document.file_name}"

    try:
        file = context.bot.getFile(file_id)
        file.download(file_name)

        result = subprocess.check_output(["./shell_script_checker.sh", file_name], text=True)
        
        if "successfully fixed" in result:
            with open(file_name, "rb") as fixed_script:
                context.bot.send_document(chat_id=update.message.chat_id, document=fixed_script, filename="fixed_" + file_name)
            result += "\n✅ Fixed script sent."
        else:
            result += "\n❌ No fixes applied." # If no fix is found
        
        update.message.reply_text(result)
    except subprocess.CalledProcessError as e:
        update.message.reply_text("⚠️ Error occurred while checking the script.")
    finally:
        os.remove(file_name) 

def examples(update, context):
    example_text = "\n\n".join([f"**{name}:**\n`\n{code}\n`" for name, code in EXAMPLES.items()])
    update.message.reply_text(f"Here are some example shell scripts:\n\n{example_text}")

def resources(update, context):
    resource_text = "\n".join(RESOURCES)
    update.message.reply_text(f"Here are some helpful resources for shell scripting:\n\n{resource_text}")

def get_system_status(update, context):
    try:
        # Ping (assuming you have 'ping' command available)
        ping_output = subprocess.check_output(["ping", "-c", "4", "google.com"], text=True)
        ping_lines = ping_output.strip().split("\n")
        ping_stats_line = ping_lines[-1]  
        ping_stats = ping_stats_line.split(" = ")[-1]

        # Uptime (Linux/macOS)
        uptime_output = subprocess.check_output(["uptime"], text=True)
        uptime = uptime_output.strip()

        status_message = f"""
**System Status**

**Ping Statistics:**
{ping_stats}

**Uptime:**
{uptime}
        """
        update.message.reply_text(status_message, parse_mode=telegram.ParseMode.MARKDOWN)
    except Exception as e:
        update.message.reply_text(f"Error retrieving system status: {e}")

def unknown(update, context):
    responses = [
        "🤔 I don't understand that command.",
        "🤷 Sorry, I'm not sure what you mean.",
        "🤖 I'm just a bot, please use a valid command."
    ]
    update.message.reply_text(random.choice(responses))

def run_other_script(update, context, script_name):
    try:
        result = subprocess.check_output(["python", script_name], text=True)
        update.message.reply_text(result)
    except subprocess.CalledProcessError as e:
        update.message.reply_text(f"Error running script: {e.stderr}")

def handle_menu_lainnya(update, context):
    keyboard = [
        [telegram.KeyboardButton("/fitur1")],
        [telegram.KeyboardButton("/fitur2")],
        # ... add more buttons for your features
    ]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard)
    update.message.reply_text("Pilih fitur:", reply_markup=reply_markup)

def handle_fitur1(update, context):
    run_other_script(update, context, "quote.py")

# --- Dispatcher Setup ---
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

# Add command handlers (start, help, check, setup, examples, resources)
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("setup", setup))
# Add the document handler for handling shell script uploads
dp.add_handler(MessageHandler(Filters.document.mime_type("text/plain"), handle_shell_script))
# Add handler for encryption and decryption commands
dp.add_handler(CommandHandler("encrypt_shell", encrypt_shell))
dp.add_handler(CommandHandler("decrypt_shell", decrypt_shell))

# Add handler for menu lainnya and its sub-features
dp.add_handler(CommandHandler("menu_lainnya", handle_menu_lainnya))
dp.add_handler(CommandHandler("fitur1", handle_fitur1))
# ... add handlers for other features (fitur2, fitur3, etc.) if needed


# Add message handlers (handle_calculation, unknown)
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_calculation)) # Handle calculation input for calculator
dp.add_handler(MessageHandler(Filters.command, unknown))  # Handle unknown commands


# Add show_handlers command (for debugging)
dp.add_handler(CommandHandler("show_handlers", show_handlers))


# Start the bot
updater.start_polling()
updater.idle()

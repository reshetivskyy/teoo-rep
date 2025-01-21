# Teoo Reputation Bot

Teoorep is a simple bot built using Python and the `telebot` library. The bot allows administrators to manage user reputation in a chat, providing commands to increase or decrease reputation, view the top users by reputation, and even earn reputation through special commands.


## Usage
- **Increase or Decrease Reputation**: Admins can increase (`/rep`) or decrease (`/norep`) a user's reputation through replies or by mentioning the user.
- **Top Reputation Board**: The `/repboard` command shows the top 5 users by reputation in the chat, along with the reputation of the user who triggered the command or the user mentioned.

## Installation

- Install the dependencies.

```sh
git clone https://github.com/reshetivskyy/teoo-rep.git
cd teoo-rep
pip install -r requirements.txt
```

- Create a .env file in the project root and add your Telegram Bot token. (TELEGRAM_BOT_TOKEN)
- And then launch the project:
```sh
py main.py
```

GLHF!
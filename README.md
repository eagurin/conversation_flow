# Conversation VoiceFlow Python

You will need Python >= 3.5 to run this code.

## Usage

### Clone this repo

```
$ git clone https://github.com/eagurin/conversation_flow.git
$ cd conversation_flow
```

### Install the requirements

```
$ python3 -m pip install -r requirements.txt
```

### To configure environment

Add a `.env` in the root directory of your project:

```
.
├── .env
└── foo.py
```

The syntax of `.env` files supported by python-dotenv is similar to that of Bash.

Set `API_KEY` and `SECRET_KEY` environment variables to your API key and secret key to authenticate
your requests to VoiceKit https://voicekit.tinkoff.ru

```bash
# Tinkoff VoiceKit https://voicekit.tinkoff.ru
API_KEY=PYeyYJ7r34AeKsO+gHQSzvX2x90AcRk29XVqdz/cm3M=
SECRET_KEY=BgUgG6oz2IrFQwxJ4Bm88r+QCoud7PBiKD8ARscmqn0=

# SQL DataBase(OpenCart 2.1.0.1)
DB_DRIVER=mysql+pymysql
DB_USERNAME=user_name
DB_PASSWORD=user_password
DB_HOST=database_host
DB_PORT=3306
DB_NAME=database_name

# Sending Online API(Russian Post)
POST_API_ACCESS_TOKEN=OO5DSt6rly6lOr1mAsQXTbrsuGdMLadU
POST_API_LOGIN_PASSWORD=ZS5hLmd1cmluQGdtYWlsLmNvbTpQNTh0YnMydXU=

```

You will probably want to add `.env` to your `.gitignore`, especially if it contains
secrets like a password.

See the section "File format" below for more information about what you can write in a
`.env` file.

### Run examples

```
$ python3 main.py
```

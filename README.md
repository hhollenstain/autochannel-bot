# AutoChannel Bot


## How to develop?

The makefile is your friend, but have a few perquisites you will need to cover first.
You will need pipenv, make, gcc (linux) for compiling fun. This readme will not go
over all this, but should be straight forward. Some info about [pipenv](https://realpython.com/pipenv-guide/#pipenv-introduction)



### Running commands

#### make init
does the base install of the source package through pipenv that should already be installed,
if a local pipenv isn't yet setup this is when it will happen (python 3.6.8)

#### make check
Designed to do linting and pipenv checking for dependencies and such

#### make test
This is designed to install fakahbot package and testing packages if I ever decided to write tests for it :shrug:

#### make dist
Makes is dist package for system built on.

#### make live
This run only on image builds in my CI/CD pipeline just install the package in the image and pushes into image repo.


### After installing fakah-bot what do?

You will need to copy example.env to .env and update the value inside

| ENV Variable | Description | Required | Default |
| :----------- | :---------: | -------: | :-----: |
| `APP_ID`     | APP ID of your discordapp | NO | N/A |
| `TOKEN`      | Token for your bots api access to discord | YES | N/A |
| `BLOCKED_USERS` | Blocked UID's of users | NO | N/A |
| `GAMES`      | Comma delimited list of games your bot is playing | NO | N/A |
| `VOICE_CHANNEL_PREFIX` | The prefix the voice channels the bot manages | NO | "!F " |


### Now Running the bot locally
run:
```bash
pipenv run autochannel
```

```bash
pipenv run autochannel
Loading .env environment variables...
[2019-08-02 17:57:20][INFO] [autochannel.autochannel_bot.main:52] LONG LIVE AutoChannel bot
[2019-08-02 17:57:20][DEBUG] [asyncio.__init__:54] Using selector: EpollSelector
[2019-08-02 17:57:20][WARNING] [discord.client.__init__:189] PyNaCl is not installed, voice will NOT be supported
[2019-08-02 17:57:20][INFO] [autochannel.lib.plugin.load:20] Loaded extension: autochannel.lib.plugins.autochannels
[2019-08-02 17:57:20][INFO] [autochannel.lib.plugin.load:20] Loaded extension: autochannel.lib.plugins.server
[2019-08-02 17:57:20][INFO] [discord.client.login:399] logging in using static token
[2019-08-02 17:57:20][INFO] [discord.gateway.from_client:241] Created websocket connected to wss://gateway.discord.gg?encoding=json&v=6&compress=zlib-stream
[2019-08-02 17:57:20][INFO] [discord.gateway.identify:320] Shard ID 0 has sent the IDENTIFY payload.
[2019-08-02 17:57:20][INFO] [discord.gateway.received_message:411] Shard ID 0 has connected to Gateway: ["gateway-prd-main-3dcm",{"micros":23263,"calls":["discord-sessions-prd-1-28",{"micros":22009,"calls":["start_session",{"micros":17988,"calls":["api-prd-main-fcsr",{"micros":15125,"calls":["get_user",{"micros":1523},"add_authorized_ip",{"micros":5},"get_guilds",{"micros":1768},"coros_wait",{"micros":2}]}]},"guilds_connect",{"micros":2,"calls":[]},"presence_connect",{"micros":3053,"calls":[]}]}]}] (Session ID: c2c093df8c212725baf89d4a596ccfe4).
[2019-08-02 17:57:22][INFO] [autochannel.lib.plugins.autochannels.on_ready:63] Starting Voice Channel purger loop
[2019-08-02 17:57:22][INFO] [autochannel.lib.plugins.server.on_ready:20] Logged in as AutoChannel-test
[2019-08-02 17:57:22][INFO] [autochannel.lib.utils.list_servers:112] Current servers: ['Tamago']
```


## Okay I got it running so?
Either fix things or change things you want. This runs on the discordpy API documentation [here](https://discordpy.readthedocs.io/en/latest/index.html)
If you want to fix things or just improve it go ahead and submit PRs against the repo, I will welcome any changes!

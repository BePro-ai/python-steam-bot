import json
import argparse
import sys
from steam.client import SteamClient
from dota2.client import Dota2Client
from dota2.features.lobby import Lobby

# Turn on console logging
import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)

GAMEMODE_NUM = {"ap": 1,
                "cm": 2,
                "rd": 3,
                "sd": 4,
                "ar": 5,
                "mo": 11,
                "1v1mid": 21}


def host_game_for(steam_ids, bot_config, lobby_config):
    # Default API classes
    client = SteamClient()
    dota = Dota2Client(client)

    # Callbacks definition
    @client.on('logged_on')
    def init():
        dota.launch()

    @dota.on('ready')
    def host_and_invite():
        # Create and configure a lobby, join the lobby channel and write "hello"
        dota.create_practice_lobby()
        dota.config_practice_lobby(lobby_config)
        client.sleep(5)  # Wait for lobby creation
        dota.channels.join_lobby_channel()
        # Invite players and move to broadcasters
        dota.join_practice_lobby_team(team=4)
        for id in steam_ids:
            dota.invite_to_lobby(id)
        # Countdown and start the game
        count = 0
        while count < bot_config["timer"]:
            client.sleep(5)
            count += 5
            dota.channels.lobby.send("%d secs until the match starts..." % (bot_config["timer"] - count))
        dota.channels.lobby.send("Beka lox")
        dota.launch_practice_lobby()
        client.sleep(60)  # Wait for lobby start
        sys.exit(0)

    # Login & cycle
    client.login(bot_config["login"], bot_config["password"])
    client.run_forever()


if __name__ == "__main__":
    # Parse command-line arguments: player ids and lobby params
    parser = argparse.ArgumentParser(
        description='Starts a bot for Dota 2 which creates a specific lobby and invites a list of players')
    parser.add_argument('ids', metavar='N', type=int, nargs='+',
                        help='players steam ids')
    parser.add_argument('--game_mode', type=str, required=False,
                        help='lobbys game mode. Available options: "ap", "cm", "rd", "sd", "ar", "mo", "1v1mid"')
    args = parser.parse_args()

    # Read bot configuration params
    with open("bot.cfg", "r") as bconfig_file:
        bot_config = json.load(bconfig_file)
    # Read main lobby configuration params
    with open("lobby.cfg", "r") as lconfig_file:
        lobby_config = json.load(lconfig_file)
    # Apply parser's values onto lobby_config
    lobby_config['game_mode'] = GAMEMODE_NUM[args.game_mode]

    # Call for main function
    host_game_for(args.ids,
                  bot_config,
                  lobby_config)

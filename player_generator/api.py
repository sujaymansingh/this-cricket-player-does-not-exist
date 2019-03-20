import random
import sys

from glob import glob
from os import getenv

from flask import Flask, redirect, render_template, url_for

from . import load_players_from_file, PlayerGenerator
from .countries import get_all_countries, get_country_by_slug
from .encodeint import decode, encode

app = Flask(__name__)


def get_latest_filename():
    filenames = glob("*.jsonl")
    filenames.sort(reverse=True)
    return filenames[0]


with open(get_latest_filename(), "r") as input_file:
    players = load_players_from_file(input_file)
    generator = PlayerGenerator(players, min_profile_length=100)


@app.route("/p/<country_slug>/<seed_str>")
def view_player(country_slug, seed_str):
    country = get_country_by_slug(country_slug)
    seed = decode(seed_str)

    (player, _seed) = generator.generate(country_id=country.country_id, seed=seed)
    return render_template("player.html", player=player)


@app.route("/random")
def random_player():
    country = random.choice(get_all_countries())

    seed = random.randint(1_000_000, 999_999_999)
    seed_str = encode(seed)

    url = url_for("view_player", country_slug=country.slug, seed_str=seed_str)
    return redirect(url)


if __name__ == "__main__":
    debug = "--debug" in sys.argv[1:]
    app.run(host="127.0.0.1", debug=debug)

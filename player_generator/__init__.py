import json
import random
import re

from sujmarkov import Markov

from .countries import get_all_countries, get_country_by_id


class PlayerGenerator():
    def __init__(self, players, min_profile_length):
        self.min_profile_length = min_profile_length

        self.profile_markov = Markov(n=3)

        self.surname_markovs = {country.country_id: Markov(n=4) for country in get_all_countries()}
        self.firstname_markovs = {country.country_id: Markov(n=4) for country in get_all_countries()}

        for player in players:
            self.add_player(player)

    def add_player(self, player):
        for line in player.profile.split("\n"):
            if line:
                sentence = line.split(" ")
                self.profile_markov.add(sentence)

        country_id = player.country_id
        self.surname_markovs[country_id].add(player.surname)

        if player.firstnames:
            for name in player.firstnames.split(" "):
                if name:
                    self.firstname_markovs[country_id].add(name)

    def generate(self, country_id=None, seed=None):
        """Returns a tuple (player, seed).
        If country_code is not passed, a random one is chosed.
        seed is used to seed the random number generator.
        This means that the same seed will always generate the same player.
        """
        if seed is None:
            seed = random.getrandbits(64)

        random_ = random.Random(seed)

        if country_id is None:
            country = random_.choice(get_all_countries())
        else:
            country = get_country_by_id(country_id)

        country_name = country.name

        surname_markov = self.surname_markovs[country_id]
        surname = "".join(surname_markov.generate(random_=random_))

        firstname_markov = self.firstname_markovs[country_id]
        firstnames_as_list = []
        for i in range(random_.choice([1, 2, 3])):
            firstname = "".join(firstname_markov.generate(random_=random_))
            firstnames_as_list.append(firstname)
        firstnames = " ".join(firstnames_as_list)

        profile = []
        while get_total_length(profile) < self.min_profile_length:
            line = " ".join(self.profile_markov.generate(random_=random_))

            for item in [
                ("$fullname", surname),
                ("$known_as", surname),
                ("$surname", surname),
                ("$firstnames", firstnames),
                ("$team", country_name),
            ]:
                placeholder, value = item
                line = line.replace(placeholder, value)
            profile.append(line)

        cleaned_profile = [line.strip() for line in profile]

        player = Player(
            country_id=country_id,
            firstnames=firstnames,
            surname=surname,
            profile=cleaned_profile,
            fullname=firstnames + " " + surname,
            known_as="")
        return (player, seed)


class Player():
    def __init__(self, country_id=None, surname="", known_as="", fullname="", profile="", firstnames=""):
        country = get_country_by_id(country_id)
        self.country_name = country.name
        self.country_id = country.country_id

        self.surname = surname
        self.known_as = known_as
        self.fullname = fullname

        if not firstnames:
            self.firstnames = get_firstnames(fullname, surname)
        else:
            self.firstnames = firstnames

        self.profile = profile

    def normalise_profile(self):
        self.profile = prepare_profile(
            self.profile,
            fullname=self.fullname,
            surname=self.surname,
            known_as=self.known_as,
            firstnames=self.firstnames,
            country_name=self.country_name)
        return self


def load_players_from_file(input_file):
    for line in input_file:
        raw_data = json.loads(line.strip())
        yield Player(**raw_data).normalise_profile()


def prepare_profile(raw_profile_lines, *, fullname, surname, known_as, firstnames, country_name):
    result = raw_profile_lines

    def _add_placeholders(profile):
        return add_placeholders(
            profile,
            fullname=fullname,
            known_as=known_as,
            surname=surname,
            firstnames=firstnames,
            country_name=country_name)

    for func in [restrict_to_safe_lines, to_single_line, _add_placeholders]:
        result = func(result)

    return result


def to_single_line(lines):
    return " ".join(lines)


def add_placeholders(line, *, fullname, known_as, surname, firstnames, country_name):
    """Given some a line, replace all specific details with placeholders.

    >>> add_placeholders(
    ...  "Mark Alan Butcher played 71 test matches for England",
    ...  fullname="", known_as="", surname="Butcher", firstnames="Mark Alan", country_name="England")
    '$firstnames $surname played 71 test matches for $team'
    """
    for (placeholder, value) in [
        ("$fullname", fullname),
        ("$known_as", known_as),
        ("$surname", surname),
        ("$firstnames", firstnames),
        ("$team", country_name),
    ]:
        if not value:
            continue

        line = line.replace(value, placeholder)

    return line


def get_firstnames(fullname, surname):
    """Assume that the fullname ends with the surname, so the rest must be the
    firstnames.

    >>> get_firstnames("Jean Paul de Beaumarche", "de Beaumarche")
    'Jean Paul'
    >>> get_firstnames("Something Odd", "Smith")
    'Something Odd'
    """
    if not fullname.endswith(surname):
        return fullname
    end = len(fullname) - len(surname)
    firstnames = fullname[:end]
    return firstnames.strip()


def restrict_to_safe_lines(lines):
    return [line for line in lines if is_profile_line_safe(line)]


def is_profile_line_safe(profile_line):
    """Return true if the profile line is 'safe'.
    We use this to remove lines that we would never want in a profile.
    """
    for banned_word in ["die", "died", "cancer", "death"]:
        pattern = re.compile(r"\b{0}\b".format(banned_word))
        if pattern.search(profile_line.strip().lower()):
            return False
    return bool(profile_line)


def get_total_length(profile):
    """Return the sum of lengths of each string in this list.

    >>> get_total_length(["This is a conversation", "Yes"])
    25
    """
    lengths = [len(line) for line in profile]
    return sum(lengths)

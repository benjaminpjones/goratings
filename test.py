from goratings.math.glicko2 import Glicko2Entry, glicko2_update
from math import exp, log
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from random import choices

START_RANK = 1150
START_DEVIATION = 350
A = 525
C = 23.15

def rank_to_rating(rank):
    return A * exp(rank / C)
def rating_to_rank(rating):
    return log(rating / A) * C

RATING_5K = rank_to_rating(25)
RATING_25K = rank_to_rating(5)

N_GAMES = 50

def rand_result(winrate):
    return choices([1, 0], [winrate, 1-winrate])[0]

def simulate(result_function):
    """Returns a list of ranks that corresponds to the results in games
    result_function takes the game info and returns (opponent, result)
    """

    user = Glicko2Entry(START_RANK, START_DEVIATION)
    ranks = []
    for i in range(N_GAMES):
        rating = user.rating
        rank = rating_to_rank(rating)
        ranks.append(rank)

        game_info = {}
        game_info["rank"] = rank
        game_info["rating"] = rating
        game_info["i"] = i

        result = result_function(game_info)

        user = glicko2_update(user, [result])
    return ranks

def winrate(rating1, rating2):
    odds = 10 ** (abs(rating1 - rating2) / 400)
    if rating1 > rating2:
        return odds / (odds + 1)
    else:
        return 1 / (odds + 1)

def only_plays_5k_and_never_wins(game_info):
    return (Glicko2Entry(RATING_5K, 65), 0)

def plays_x_rank_only(rank):
    RATING = rank_to_rating(rank)
    def f(game_info):
        return (Glicko2Entry(RATING, 65), rand_result(winrate(RATING_25K, RATING)))
    return f

def plays_proper_matches(game_info):
    rating = game_info["rating"]
    result = rand_result(winrate(RATING_25K, rating))
    return (Glicko2Entry(rating, 65), result)

def wins_a_few_at_the_start(game_info):
    i = game_info["i"]
    if i < 1:
        return (Glicko2Entry(game_info["rating"], 65), 1)
    else:
        return plays_proper_matches(game_info)

def plays_x_stones_stronger(stones):
    def f(game_info):
        rank = game_info["rank"]
        rank = rank + stones
        rating = rank_to_rating(rank)
        result = rand_result(winrate(RATING_25K, rating))
        return (Glicko2Entry(rating, 65), result)
    return f

def simulate_averaged(f):
    """Just like simulate, but attempts to mitigate randomness through averaging"""
    trials = 500
    rank_totals = [0] * N_GAMES
    for i in range(trials):
        ranks = simulate(f)
        for i in range(N_GAMES):
            rank_totals[i] += ranks[i]
    return [ tot / trials for tot in rank_totals ]

result_functions = [
    # only_plays_5k_and_never_wins,
    ("Even matchups only", plays_proper_matches),
    # ("Wins 3 at start", wins_a_few_at_the_start),
    # ("Plays only 5k (impossible)", plays_x_rank_only(25)),
    ("Plays 9 stones down", plays_x_stones_stronger(-9)),
    ("Plays only 25k (impossible)", plays_x_rank_only(5)),
    # ("Plays 5 stones up", plays_x_stones_stronger(5)),
]


for f in result_functions:
    line, = plt.plot(simulate_averaged(f[1]))
    line.set_label(f[0])

@mticker.FuncFormatter
def kyu_formatter(rank, pos):
    return f"{30-rank:.1f}k"

plt.gca().yaxis.set_major_formatter(kyu_formatter)
plt.yticks([0, 5, 10, 15, 20])
plt.gca().legend()
 
plt.axhline(y = 8, color = 'b', linestyle = ':', label = "20k") 
plt.axhline(y = 5, color = 'r', linestyle = '--', label = "25k") 

plt.ylim(0, 22)
plt.xlim(0, N_GAMES)
  
plt.show()

print(rating_to_rank(400))
print(winrate(RATING_5K, RATING_25K))

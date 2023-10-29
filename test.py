from goratings.math.glicko2 import Glicko2Entry, glicko2_update
from analysis.util.RatingMath import rating_to_rank, rank_to_rating
from math import exp, log
import matplotlib.pyplot as plt
from random import choices

START_RANK = 1150
START_DEVIATION = 350
A = 525
C = 23.15

def rank_to_rating(rank):
    return A * exp(rank / C)
def rating_to_rank(rating):
    return log(rating / A) * C

RATING_25K = rank_to_rating(5)

# this is a user who only plays (established) SDK
user = Glicko2Entry(START_RANK, START_DEVIATION)
ranks = []
for i in range(300):
    rank = rating_to_rank(user.rating)
    ranks.append(rank)
    user = glicko2_update(user, [(Glicko2Entry(rating=1500, deviation=65), 0)])

# this is a user who plays evenly ranked players, but won their first 10 matches
user2 = Glicko2Entry(START_RANK, START_DEVIATION)
ranks2 = []
for i in range(290):
    rating = user2.rating
    rank = rating_to_rank(user2.rating)
    ranks2.append(rank)

    odds = 10 ** (abs(rating - RATING_25K) / 400) 
    RATING_25K = rank_to_rating(5)
    if rating > RATING_25K:
        winrate = 1 / (odds + 1)
    else:
        winrate = odds / (odds + 1)

    result = choices([1, 0], [winrate, 1-winrate])[0]
    print(result)
    
    user2 = glicko2_update(user2, [(Glicko2Entry(rating=user2.rating, deviation=65), result)])
    print(user2)

def rand_result(winrate):
    return choices([1, 0], [winrate, 1-winrate])[0]

def simulate(result_function):
    """Returns a list of ranks that corresponds to the results in games
    result_function takes the game info and returns (opponent, result)
    """

    user = Glicko2Entry(START_RANK, START_DEVIATION)
    ranks = []
    for i in range(300):
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

def winrate(rank1, rank2):
    rating1, rating2 = rank_to_rating(rank1), rank_to_rating(rank2)
    odds = 10 ** (abs(rating1 - rating2) / 400)
    if rating1 > rating2:
        return odds / (odds + 1)
    else:
        return 1 / (odds + 1)

def only_plays_5k_and_never_wins(game_info):
    rating_5k = rank_to_rating(25)
    return (Glicko2Entry(rating_5k, 65), 0)

def plays_5k_and_wins_occasionally(game_info):
    rating_5k = rank_to_rating(25)
    return (Glicko2Entry(rating_5k, 65), rand_result(winrate(5, 25)))

def plays_proper_matches(game_info):
    rank = game_info["rank"]
    result = rand_result(winrate(5, rank))
    return (Glicko2Entry(game_info["rating"], 65), result)

def wins_a_few_at_the_start(game_info):
    i = game_info["i"]
    if i < 3:
        return (Glicko2Entry(game_info["rating"], 65), 1)
    else:
        return plays_proper_matches(game_info)

result_functions = [
    only_plays_5k_and_never_wins,
    plays_proper_matches,
    wins_a_few_at_the_start,
    plays_5k_and_wins_occasionally,
]

for f in result_functions:
    plt.plot(simulate(f))
plt.show()

print(rating_to_rank(400))

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


plt.plot(ranks)
plt.plot(ranks2)
plt.show()

print(rating_to_rank(400))


import ssa

primes_list = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
    67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131,
]

class Poll:
    prime = 2 ** 2203 - 1
    def __init__(self, nauth, options, question = "?"):
        self.question = question
        self.shamir = ssa.Shamir(nauth // 2, Poll.prime)
        (self.weights, self.options) = self.gen_options(options)
        self.authorities = self.gen_authorities(nauth)
        self.votes = 0
        print("Question: \"" + self.question + "\"")
        print("Possible answers:", options)

    def vote(self, ballot):
        assert (self.votes < self.max_votes()), (
            "Maximum number of voters reached (%s)" % self.votes
        )
        self.votes += 1
        vote = self.weights[ballot]
        shares = self.shamir.shares_for(vote, self.keyset)
        self.compute_vote(shares)

    def results(self):
        print("\nNumber of voters:", self.votes)
        print("\nResults:\n")
        shares = {a.key : a.votes for a in self.authorities}
        result = self.shamir.reconstruct(shares)
        score = self.get_score(result)
        for (weight, votes) in score.items():
            print(self.options[weight] + ":", votes)

# Constraints over ShamirNPoll:
# Be P the prime used by ShamirNPoll, N the number of authorities, Z the
# maximum prime value in options and V the number of voters, the following
# conditions must hold:
#   N < P
#   Z ** V < P
# Shamir's threshold is always N // 2, due to the use of multiplication
# over the shares, resulting in a 2t degree polinomial.

# primes_list contains all possible values for options and ShamirNPoll.prime
# defines the prime used by Shamir, therefore:
# Z = 131
# P = 2 ** 2203 - 1
# Maximum number of options = 32, since len(primes_list) == 32
# Maximum number of voters = 181, since (131 ** 182) > (2 ** 2203 - 1)
# and (131 ** 181) < (2 ** 2203 - 1)
class ShamirNPoll(Poll):
    def gen_options(self, options):
        assert (len(options) <= len(primes_list)), (
            "ShamirNPoll supports at most %s options" % len(primes_list)
        )
        weights = {}
        symbols = {}
        for i, option in enumerate(options):
            symbols[primes_list[i]] = option
            weights[option] = primes_list[i]
        return (weights, symbols)

    def gen_authorities(self, nauth):
        assert (nauth < self.prime), (
            "Number of authorities must be smaller than %s" % self.prime
        )
        self.keyset = ssa.gen_entries(nauth, self.prime)
        betas = ssa.lagrange_betas(self.keyset, self.prime)
        authorities = []
        for i in range(nauth):
            authorities.append(
                self.Authority(self, self.keyset[i], betas[i])
            )
        return authorities

    def max_votes(self):
        return 181

    def compute_vote(self, shares):
        self.__shared_memory = {}
        if self.votes == 1:
            for a in self.authorities:
                a.votes = shares[a.key]
        else:
            for a in self.authorities:
                a.precompute_vote(shares[a.key])

            for a in self.authorities:
                shares = [s[1][a.key] for s in self.__shared_memory.items()]
                a.consolidate_vote(shares)

    def get_score(self, result):
        return factorize(result, self.options.keys())

    def broadcast(self, key, accum):
        shares = self.shamir.shares_for(accum, self.keyset)
        self.__shared_memory[key] = shares

    class Authority:
        def __init__(self, poll, key, beta):
            self.key = key
            self.beta = beta
            self.poll = poll
            self.votes = None

        def precompute_vote(self, share):
            accum = self.votes * share * self.beta
            self.poll.broadcast(self.key, accum)

        def consolidate_vote(self, broadcast):
            self.votes = 0
            for value in broadcast:
                self.votes += value

class Shamir2Poll(Poll):
    def gen_options(self, options):
        assert (len(options) == 2), (
            "Shamir2Poll supports only 2 options"
        )
        weights = {}
        symbols = {}
        for i, option in enumerate(options):
            symbols[i] = option
            weights[option] = i
        return (weights, symbols)

    def gen_authorities(self, nauth):
        assert (nauth < self.prime), (
            "Number of authorities must be smaller than %s" % self.prime
        )
        self.keyset = ssa.gen_entries(nauth, self.prime)
        authorities = []
        for i in range(nauth):
            authorities.append(self.Authority(self.keyset[i]))
        return authorities

    def max_votes(self):
        return self.prime - 1

    def compute_vote(self, shares):
        for a in self.authorities:
            a.compute_vote(shares[a.key])

    def get_score(self, result):
        return {0 : self.votes - result, 1 : result}

    class Authority:
        def __init__(self, key,):
            self.key = key
            self.votes = 0

        def compute_vote(self, share):
            self.votes += share

def factorize(number, primes):
    factors = {}
    for prime in primes:
        factors[prime] = 0
        while number != 0 and number % prime == 0:
            factors[prime] += 1
            number = number // prime
    return factors

if __name__ == "__main__":
    poll = ShamirNPoll(
        nauth = 30,
        options = ["Sure!", "Yes", "No.", "Maybe?"],
        question = "Does ShamirNPoll work?"
    )

    print("\nVoting...")

    poll.vote("Yes")
    poll.vote("No.")
    poll.vote("No.")
    poll.vote("No.")
    poll.vote("No.")
    poll.vote("Yes")
    poll.vote("Yes")
    poll.vote("Yes")
    poll.vote("Maybe?")
    poll.vote("Yes")
    poll.vote("Sure!")
    poll.vote("Maybe?")
    poll.vote("Maybe?")
    poll.vote("Sure!")
    poll.vote("Sure!")
    poll.vote("Yes")
    poll.vote("Yes")
    poll.vote("Yes")
    poll.vote("No.")
    poll.vote("No.")
    poll.vote("Sure!")
    poll.results()

    poll = Shamir2Poll(
        nauth = 100,
        options = ["Yes", "No"],
        question = "Does Shamir2Poll work?"
    )

    print("\nVoting...")

    poll.vote("Yes")
    poll.vote("No")
    poll.vote("No")
    poll.vote("No")
    poll.vote("No")
    poll.vote("Yes")
    poll.vote("Yes")
    poll.vote("Yes")
    poll.vote("No")
    poll.vote("Yes")
    poll.vote("Yes")
    poll.vote("No")
    poll.vote("No")
    poll.vote("Yes")
    poll.vote("Yes")
    poll.vote("Yes")
    poll.vote("Yes")
    poll.vote("Yes")
    poll.vote("No")
    poll.vote("No")
    poll.vote("Yes")
    poll.results()


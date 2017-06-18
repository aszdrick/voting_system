
import ssa

primes_list = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
    67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131,
]

# Constraints over ShamirPoll:
# Be P the prime used by ShamirPoll, N the number of authorities, Z the
# maximum prime value in options and V the number of voters, the following
# conditions must hold:
#   N < P
#   Z ** V < P
# Shamir's threshold is always N // 2, due to the use of multiplication
# over the shares, resulting in a 2t degree polinomial.

# primes_list contains all possible values for options and ShamirPoll.prime
# defines the prime used by Shamir, therefore:
# Z = 131
# P = 2 ** 2203 - 1
# Maximum number of options = 32, since len(primes_list) == 32
# Maximum number of voters = 181, since (131 ** 182) > (2 ** 2203 - 1)
# and (131 ** 181) < (2 ** 2203 - 1)
class ShamirPoll:
    prime = 2 ** 2203 - 1
    def __init__(self, nauth, options, question = "?"):
        self.question = question
        self.shamir = ssa.Shamir(nauth // 2, ShamirPoll.prime)
        (self.weights, self.options) = self.gen_options(options)
        self.authorities = self.gen_authorities(nauth)
        self.votes = 0
        print("Question: \"" + self.question + "\"")
        print("Possible answers:", options)

    def gen_options(self, options):
        assert (len(options) <= len(primes_list)), (
            "ShamirPoll supports at most %s options" % len(primes_list)
        )
        weights = {}
        symbols = {}
        for i, option in enumerate(options):
            symbols[primes_list[i]] = option
            weights[option] = primes_list[i]
        return (weights, symbols)

    def gen_authorities(self, nauth):
        assert (nauth < self.prime), (
            "Number of autorithies must be smaller than %s" % self.prime
        )
        self.keyset = ssa.gen_entries(nauth, self.prime)
        betas = ssa.lagrange_betas(self.keyset, self.prime)
        autorithies = []
        for i in range(nauth):
            autorithies.append(
                self.Authority(self, self.keyset[i], betas[i])
            )
        return autorithies

    def vote(self, ballot):
        self.__shared_memory = {}
        assert (self.votes < 181), (
            "Maximum number of voters reached (%s)" % self.votes
        )
        self.votes += 1
        vote = self.weights[ballot]
        shares = self.shamir.shares_for(vote, self.keyset)
        if self.votes == 1:
            for a in self.authorities:
                a.votes = shares[a.key]
        else:
            for a in self.authorities:
                a.precompute_vote(shares[a.key])

            for a in self.authorities:
                shares = [s[1][a.key] for s in self.__shared_memory.items()]
                a.consolidate_vote(shares)

    def results(self):
        print("Number of voters:", self.votes)
        print("\nResults:\n")
        shares = {a.key : a.votes for a in self.authorities}
        product = self.shamir.reconstruct(shares)
        score = factorize(product, self.options.keys())
        for (weight, votes) in score.items():
            print(self.options[weight] + ":", votes)

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

def factorize(number, primes):
    factors = {}
    for prime in primes:
        factors[prime] = 0
        while number != 0 and number % prime == 0:
            factors[prime] += 1
            number = number // prime
    return factors

if __name__ == "__main__":
    poll = ShamirPoll(
        30, ["Sure!", "Yes", "No.", "Maybe?"],
        "Does ShamirPoll work?"
    )

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

import readline
import secrets

def inverse(a, p):
    t = 0
    r = p
    newt = 1
    newr = a
    while newr != 0:
        quotient = r // newr
        (t, newt) = (newt, t - quotient * newt)
        (r, newr) = (newr, r - quotient * newr)
    assert (r <= 1), "%s is not invertible" % (a)
    if t < 0:
        t = t + p
    return t

def gen_entries(n, prime):
    return list(range(1, n + 1))

def gen_coefs(constant, n, prime):
    coefs = [constant]
    for i in range(n):
        coefs.append(secrets.randbelow(prime))
    return coefs

def lagrange_betas(entries):
    betas = []
    for xj in entries:
        product = 1;
        for xm in [xm for xm in entries if xm != xj]:
            d = (xm - xj) % self.prime
            product = (product * xm * inverse(d, self.prime)) % self.prime
        betas.append(product)
    return betas

class Shamir:
    def __init__(self, threshold, prime):
        self.t = threshold
        self.prime = prime

    def polinomial(self, x):
        result = self.coefs[0]
        x_power = x
        for c in self.coefs[1:]:
            result = (result + c * x_power) % self.prime
            x_power = (x_power * x) % self.prime
        return result % self.prime

    def shares(self, secret, n, entries = None):
        if not entries:
            entries = gen_entries(n, self.prime)
        self.coefs = gen_coefs(secret, self.t - 1, self.prime)
        shares = []
        for entry in entries:
            shares.append((entry, self.polinomial(entry)))
        return shares

    def reconstruct(self, shares):
        assert (len(shares) >= self.t), "Insufficient number of shares"
        result = 0
        for (x, y) in shares:
            product = 1;
            for xm in [xm for (xm, __) in shares if xm != x]:
                d = (xm - x) % self.prime
                product = (product * xm * inverse(d, self.prime)) % self.prime
            result = (result + y * product) % self.prime
        return result

if __name__ == "__main__":
    secret = int(input("Secret to share: "))
    threshold = int(input("Threshold: "))
    prime = int(input("Prime number: "))
    participants = int(input("Number of participants: "))
    print("original secret = %d" % secret)
    print("threshold = %d" % threshold)
    print("prime = %d" % prime)
    print("participants = %d" % participants)
    shamir = Shamir(threshold, prime)
    shares = shamir.shares(secret, participants)
    # print("shares = %s" % shares)
    secret = shamir.reconstruct(shares[:threshold])
    print("recovered secret = %d" % secret)

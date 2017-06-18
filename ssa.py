import readline
import secrets

class Shamir:
    def __init__(self, threshold, prime):
        self.t = threshold
        self.prime = prime

    def get_polinomial(self, secret, coeffs = None):
        return self.Polinomial(self, secret, coeffs)

    def n_shares(self, secret, n, polinomial = None):
        entries = gen_entries(n, self.prime)
        if polinomial is None:
            polinomial = self.get_polinomial(secret)
        shares = {}
        for entry in entries:
            shares[entry] = polinomial(entry)
        return shares

    def shares_for(self, secret, entries, polinomial = None):
        if polinomial is None:
            polinomial = self.get_polinomial(secret)
        return {x : polinomial(x) for x in entries}

    def reconstruct(self, shares):
        assert (len(shares) >= self.t), ("Insufficient number of shares")
        result = 0
        for (x, y) in shares.items():
            product = 1;
            for xm in [xm for (xm, __) in shares.items() if xm != x]:
                d = (xm - x) % self.prime
                product = (product * xm * inverse(d, self.prime)) % self.prime
            result = (result + y * product) % self.prime
        return result

    class Polinomial:
        def __init__(self, shamir, secret, coeffs = None):
            self.prime = shamir.prime
            self.coeffs = coeffs
            if self.coeffs is None:
                self.coeffs = gen_coeffs(secret, shamir.t - 1, shamir.prime)
            assert (len(self.coeffs) == shamir.t), (
                "Wrong number of coefficients"
            )

        def __call__(self, x):
            result = self.coeffs[0]
            x_power = x
            for c in self.coeffs[1:]:
                result = (result + c * x_power) % self.prime
                x_power = (x_power * x) % self.prime
            return result % self.prime

def inverse(a, p):
    t = 0
    r = p
    newt = 1
    newr = a
    while newr != 0:
        quotient = r // newr
        (t, newt) = (newt, t - quotient * newt)
        (r, newr) = (newr, r - quotient * newr)
    assert (r <= 1), ("%s is not invertible" % (a))
    if t < 0:
        t = t + p
    return t

def gen_entries(n, prime):
    return list(range(1, n + 1))

def gen_coeffs(constant, n, prime):
    coeffs = [constant]
    for i in range(n):
        coeffs.append(secrets.randbelow(prime))
    return coeffs

def lagrange_betas(entries, prime):
    betas = []
    for xj in entries:
        product = 1;
        for xm in [xm for xm in entries if xm != xj]:
            d = (xm - xj) % prime
            product = (product * xm * inverse(d, prime)) % prime
        betas.append(product)
    return betas

if __name__ == "__main__":
    # secret = int(input("Secret to share: "))
    # threshold = int(input("Threshold: "))
    # prime = int(input("Prime number: "))
    # participants = int(input("Number of participants: "))
    # print("original secret = %d" % secret)
    # print("threshold = %d" % threshold)
    # print("prime = %d" % prime)
    # print("participants = %d" % participants)
    # shamir = Shamir(threshold, prime)
    # shares = shamir.shares(secret, participants)
    # # print("shares = %s" % shares)
    # secret = shamir.reconstruct(shares[:threshold])
    # print("recovered secret = %d" % secret)

    shamir = Shamir(5, 2 ** 2203 - 1)
    entries = gen_entries(100, 2 ** 2203 - 1)
    betas = lagrange_betas(entries, 2 ** 2203 - 1)
    v1 = shamir.shares_for(5, entries)
    v2 = shamir.shares_for(5, entries)

    mult = []
    zs = {}

    for i in entries:
        z = v1[i] * v2[i] * betas[i - 1]
        zshares = shamir.shares_for(z, entries)
        zs[i] = zshares

    for i in entries:
        accum = 0
        for j in entries:
            accum += zs[j][i]
        v1[i] = accum

    secret = shamir.reconstruct(v1)
    print(secret)
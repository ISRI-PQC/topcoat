# MIT License

# Copyright (c) 2022 Giacomo Pope

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
The class `NTTHelper` has been defined to allow for the
`Polynomial` class to have some `n=256` NTT help for
Dilithium. This is ok code, but it doesnt generalise nicely.

TODOs:

- Build structure to allow this to generalise away from n=256.

"""

NTT_PARAMETERS = {
    "dilithium": {
        "q": 8380417,
        "q_inv": 58728449,  # q^(-1) mod 2^32
        "mont_r": 4193792,  # 2^32 mod q
        "mont_r2": 2365951,  # 2^64 mod q
        "mont_r_inv": 8265825,  # (1 / 2^32) mod q
        "mont_mask": (1 << 32) - 1,
        # "root_of_unity" : 1753,
        # zetas  : [(mont_r * pow(root_of_unity,  br(i,8), q)) % q for i in range(256)],
        "zetas": [
            4193792,
            25847,
            5771523,
            7861508,
            237124,
            7602457,
            7504169,
            466468,
            1826347,
            2353451,
            8021166,
            6288512,
            3119733,
            5495562,
            3111497,
            2680103,
            2725464,
            1024112,
            7300517,
            3585928,
            7830929,
            7260833,
            2619752,
            6271868,
            6262231,
            4520680,
            6980856,
            5102745,
            1757237,
            8360995,
            4010497,
            280005,
            2706023,
            95776,
            3077325,
            3530437,
            6718724,
            4788269,
            5842901,
            3915439,
            4519302,
            5336701,
            3574422,
            5512770,
            3539968,
            8079950,
            2348700,
            7841118,
            6681150,
            6736599,
            3505694,
            4558682,
            3507263,
            6239768,
            6779997,
            3699596,
            811944,
            531354,
            954230,
            3881043,
            3900724,
            5823537,
            2071892,
            5582638,
            4450022,
            6851714,
            4702672,
            5339162,
            6927966,
            3475950,
            2176455,
            6795196,
            7122806,
            1939314,
            4296819,
            7380215,
            5190273,
            5223087,
            4747489,
            126922,
            3412210,
            7396998,
            2147896,
            2715295,
            5412772,
            4686924,
            7969390,
            5903370,
            7709315,
            7151892,
            8357436,
            7072248,
            7998430,
            1349076,
            1852771,
            6949987,
            5037034,
            264944,
            508951,
            3097992,
            44288,
            7280319,
            904516,
            3958618,
            4656075,
            8371839,
            1653064,
            5130689,
            2389356,
            8169440,
            759969,
            7063561,
            189548,
            4827145,
            3159746,
            6529015,
            5971092,
            8202977,
            1315589,
            1341330,
            1285669,
            6795489,
            7567685,
            6940675,
            5361315,
            4499357,
            4751448,
            3839961,
            2091667,
            3407706,
            2316500,
            3817976,
            5037939,
            2244091,
            5933984,
            4817955,
            266997,
            2434439,
            7144689,
            3513181,
            4860065,
            4621053,
            7183191,
            5187039,
            900702,
            1859098,
            909542,
            819034,
            495491,
            6767243,
            8337157,
            7857917,
            7725090,
            5257975,
            2031748,
            3207046,
            4823422,
            7855319,
            7611795,
            4784579,
            342297,
            286988,
            5942594,
            4108315,
            3437287,
            5038140,
            1735879,
            203044,
            2842341,
            2691481,
            5790267,
            1265009,
            4055324,
            1247620,
            2486353,
            1595974,
            4613401,
            1250494,
            2635921,
            4832145,
            5386378,
            1869119,
            1903435,
            7329447,
            7047359,
            1237275,
            5062207,
            6950192,
            7929317,
            1312455,
            3306115,
            6417775,
            7100756,
            1917081,
            5834105,
            7005614,
            1500165,
            777191,
            2235880,
            3406031,
            7838005,
            5548557,
            6709241,
            6533464,
            5796124,
            4656147,
            594136,
            4603424,
            6366809,
            2432395,
            2454455,
            8215696,
            1957272,
            3369112,
            185531,
            7173032,
            5196991,
            162844,
            1616392,
            3014001,
            810149,
            1652634,
            4686184,
            6581310,
            5341501,
            3523897,
            3866901,
            269760,
            2213111,
            7404533,
            1717735,
            472078,
            7953734,
            1723600,
            6577327,
            1910376,
            6712985,
            7276084,
            8119771,
            4546524,
            5441381,
            6144432,
            7959518,
            6094090,
            183443,
            7403526,
            1612842,
            4834730,
            7826001,
            3919660,
            8332111,
            7018208,
            3937738,
            1400424,
            7534263,
            1976782,
        ],
        "f": 41978,  # 2^64 / 256 % q
    },
    "topcoat": {
        "q": 8380417,
        "q_inv": 58728449,  # q^(-1) mod 2^32
        "mont_r": 4193792,  # 2^32 mod q
        "mont_r2": 2365951,  # 2^64 mod q
        "mont_r_inv": 8265825,  # (1 / 2^32) mod q
        "mont_mask": (1 << 32) - 1,
        # "root_of_unity" : 1753,
        # zetas  : [(mont_r * pow(root_of_unity,  br(i,8), q)) % q for i in range(256)],
        "zetas": [
            0,
            25847,
            -2608894,
            -518909,
            237124,
            -777960,
            -876248,
            466468,
            1826347,
            2353451,
            -359251,
            -2091905,
            3119733,
            -2884855,
            3111497,
            2680103,
            2725464,
            1024112,
            -1079900,
            3585928,
            -549488,
            -1119584,
            2619752,
            -2108549,
            -2118186,
            -3859737,
            -1399561,
            -3277672,
            1757237,
            -19422,
            4010497,
            280005,
            2706023,
            95776,
            3077325,
            3530437,
            -1661693,
            -3592148,
            -2537516,
            3915439,
            -3861115,
            -3043716,
            3574422,
            -2867647,
            3539968,
            -300467,
            2348700,
            -539299,
            -1699267,
            -1643818,
            3505694,
            -3821735,
            3507263,
            -2140649,
            -1600420,
            3699596,
            811944,
            531354,
            954230,
            3881043,
            3900724,
            -2556880,
            2071892,
            -2797779,
            -3930395,
            -1528703,
            -3677745,
            -3041255,
            -1452451,
            3475950,
            2176455,
            -1585221,
            -1257611,
            1939314,
            -4083598,
            -1000202,
            -3190144,
            -3157330,
            -3632928,
            126922,
            3412210,
            -983419,
            2147896,
            2715295,
            -2967645,
            -3693493,
            -411027,
            -2477047,
            -671102,
            -1228525,
            -22981,
            -1308169,
            -381987,
            1349076,
            1852771,
            -1430430,
            -3343383,
            264944,
            508951,
            3097992,
            44288,
            -1100098,
            904516,
            3958618,
            -3724342,
            -8578,
            1653064,
            -3249728,
            2389356,
            -210977,
            759969,
            -1316856,
            189548,
            -3553272,
            3159746,
            -1851402,
            -2409325,
            -177440,
            1315589,
            1341330,
            1285669,
            -1584928,
            -812732,
            -1439742,
            -3019102,
            -3881060,
            -3628969,
            3839961,
            2091667,
            3407706,
            2316500,
            3817976,
            -3342478,
            2244091,
            -2446433,
            -3562462,
            266997,
            2434439,
            -1235728,
            3513181,
            -3520352,
            -3759364,
            -1197226,
            -3193378,
            900702,
            1859098,
            909542,
            819034,
            495491,
            -1613174,
            -43260,
            -522500,
            -655327,
            -3122442,
            2031748,
            3207046,
            -3556995,
            -525098,
            -768622,
            -3595838,
            342297,
            286988,
            -2437823,
            4108315,
            3437287,
            -3342277,
            1735879,
            203044,
            2842341,
            2691481,
            -2590150,
            1265009,
            4055324,
            1247620,
            2486353,
            1595974,
            -3767016,
            1250494,
            2635921,
            -3548272,
            -2994039,
            1869119,
            1903435,
            -1050970,
            -1333058,
            1237275,
            -3318210,
            -1430225,
            -451100,
            1312455,
            3306115,
            -1962642,
            -1279661,
            1917081,
            -2546312,
            -1374803,
            1500165,
            777191,
            2235880,
            3406031,
            -542412,
            -2831860,
            -1671176,
            -1846953,
            -2584293,
            -3724270,
            594136,
            -3776993,
            -2013608,
            2432395,
            2454455,
            -164721,
            1957272,
            3369112,
            185531,
            -1207385,
            -3183426,
            162844,
            1616392,
            3014001,
            810149,
            1652634,
            -3694233,
            -1799107,
            -3038916,
            3523897,
            3866901,
            269760,
            2213111,
            -975884,
            1717735,
            472078,
            -426683,
            1723600,
            -1803090,
            1910376,
            -1667432,
            -1104333,
            -260646,
            -3833893,
            -2939036,
            -2235985,
            -420899,
            -2286327,
            183443,
            -976891,
            1612842,
            -3545687,
            -554416,
            3919660,
            -48306,
            -1362209,
            3937738,
            1400424,
            -846154,
            1976782,
        ],
        "f": 41978,
    },
}


class NTTHelper:
    def __init__(self, parameter_set):
        self.q = parameter_set["q"]
        self.q_inv = parameter_set["q_inv"]
        self.mont_r = parameter_set["mont_r"]
        self.mont_r2 = parameter_set["mont_r2"]
        self.mont_r_inv = parameter_set["mont_r_inv"]
        self.mont_mask = parameter_set["mont_mask"]
        self.zetas = parameter_set["zetas"]
        self.f = parameter_set["f"]

    @staticmethod
    def br(i, k):
        """
        bit reversal of an unsigned k-bit integer
        """
        bin_i = bin(i & (2**k - 1))[2:].zfill(k)
        return int(bin_i[::-1], 2)

    def montgomery_reduce(self, a):
        """
        a -> R^(-1) a mod q
        """
        # t = (a * self.q_inv) & self.mont_mask
        # t = (a - (t * self.q)) >> 32
        # if t <= -(self.q - 1) >> 2:
        #     t += self.q
        r = (a * self.mont_r_inv) % self.q
        if r > (self.q >> 1):
            r -= self.q
        # if not r > -(self.q >> 1):
        #    print(f"{r}, { -(self.q >> 1)}, {self.q}")
        # if not r <= (self.q >> 1):
        #     print(f"{r}, {(self.q >> 1)}, {self.q}")
        return r

    def to_montgomery(self, poly):
        poly.coeffs = [self.ntt_mul(self.mont_r2, c) for c in poly.coeffs]
        return poly

    def from_montgomery(self, poly):
        poly.coeffs = [self.montgomery_reduce(c) for c in poly.coeffs]
        return poly

    def ntt_mul(self, a, b):
        """
        Multiplication then Montgomery reduction

        Ra * Rb -> Rab
        """
        c = a * b
        return self.montgomery_reduce(c)

    def ntt_coefficient_multiplication(self, f_coeffs, g_coeffs):
        return [self.ntt_mul(c1, c2) for c1, c2 in zip(f_coeffs, g_coeffs)]

    def to_ntt(self, poly):
        """
        Convert a polynomial to number-theoretic transform (NTT) form in place
        The input is in standard order, the output is in bit-reversed order.
        NTT_ZETAS also has the Montgomery factor 2^16 included, so NTT
        additionally maps to Montgomery domain.

        Only implemented (currently) for n = 256
        """
        if poly.is_ntt:
            raise ValueError("Cannot convert NTT form polynomial to NTT form")

        k, l = 0, 128
        coeffs = poly.coeffs
        while l > 0:
            start = 0
            while start < 256:
                k = k + 1
                zeta = self.zetas[k]
                for j in range(start, start + l):
                    t = self.ntt_mul(zeta, coeffs[j + l])
                    coeffs[j + l] = coeffs[j] - t
                    coeffs[j] = coeffs[j] + t
                start = l + (j + 1)
            l >>= 1

        poly.is_ntt = True
        return poly

    def from_ntt(self, poly):
        """
        Convert a polynomial from number-theoretic transform (NTT) form in place
        and multiplication by Montgomery factor 2^16.
        The input is in bit-reversed order, the output is in standard order.

        Because of the montgomery multiplication, we have:
            f != f.to_ntt().from_ntt()
            f = (1/2^16) * f.to_ntt().from_ntt()

        To recover f we do
            f == f.to_ntt().from_ntt().from_montgomery()

        Only implemented (currently) for n = 256
        """
        if not poly.is_ntt:
            raise ValueError("Can only convert from a polynomial in NTT form")

        l, k = 1, 256
        coeffs = poly.coeffs
        while l < 256:
            start = 0
            while start < 256:
                k = k - 1
                zeta = -self.zetas[k]
                for j in range(start, start + l):
                    t = coeffs[j]
                    coeffs[j] = t + coeffs[j + l]
                    coeffs[j + l] = t - coeffs[j + l]
                    coeffs[j + l] = self.ntt_mul(zeta, coeffs[j + l])
                start = j + l + 1
            l = l << 1
        for j in range(256):
            coeffs[j] = self.ntt_mul(coeffs[j], self.f)

        poly.is_ntt = False
        return poly


NTTHelperDilithium = NTTHelper(NTT_PARAMETERS["dilithium"])
NTTHelperTopcoat = NTTHelper(NTT_PARAMETERS["topcoat"])

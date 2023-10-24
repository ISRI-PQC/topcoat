package crypto;

import java.util.Arrays;
import java.security.SecureRandom;
import java.io.Serializable;
import java.lang.Math;
import org.bouncycastle.crypto.digests.SHAKEDigest;


public class Poly implements Serializable {
	
	/*
	 * add() - Poly
	 * sub() - Poly
	 * multiplyByConst() - Poly
	 * mod - void
	 * invnttTomont - void
	 * reduce - Poly
	 * ntt - void
	 * caddq - void
	 * centeredMod 
	 */
	
	
	private static final long serialVersionUID = -8569061490237245674L;
	public int[] coefficients;
	public int polyLength;
	
	/*****
	 * 
	Creates "empty" polynomial of size n 
	(a_n*x^n + a_{n-1}*x^{n-1}... + a_1*n + a_0. 
	a_i - element of  int[] coefficients) 

	*****/
	
	// Constructors
	
	public Poly(int n) {
		this.coefficients = new int[n];
		this.polyLength = n; 
	}
	
	public Poly() {
		this.coefficients = new int[Params.N];
		this.polyLength = Params.N;
	}
	
	
	// Addition and subtraction 
	// All algebra is done modulo Q
	
	public Poly add(Poly x) {
		Poly ans = new Poly(x.polyLength);
		for (int i = 0; i < x.polyLength; i++) {
			ans.coefficients[i] = (this.coefficients[i] + x.coefficients[i]) % Params.Q;
		}
		return ans;
	}
	
	public Poly sub(Poly x) {
		Poly ans = new Poly(x.polyLength);
		for (int i = 0; i < x.polyLength; i++) {
			ans.coefficients[i] = (this.coefficients[i] - x.coefficients[i]) % Params.Q;
		}
		return ans;
	}
	
	//Needed for hint, might not work for poly with coefficients in bigger range due to overflow
	
	public Poly multiplyByConst(int c) {
		Poly ans = new Poly(this.polyLength);
		for (int i = 0; i < this.polyLength; i++) {
			ans.coefficients[i] = (this.coefficients[i] * c) % Params.Q;
		}
		return ans;
	}
	
	// Makes all coefficients non-negative
	public void caddq() {
		for (int i = 0; i < coefficients.length; i++) {
			coefficients[i] = caddq(coefficients[i]);
		}

	}
	
	// Add Q if input coefficient is negative.
	private int caddq(int a) {
		a += (a >> 31) & Params.Q;
		return a;
	}
	
	
	// Does modulo m reduction for whole Poly
	public void mod(int m) {
		for (int i=0; i < this.polyLength; i++) {
			int x = this.coefficients[i];
			x = Math.floorMod(x, m);
			this.coefficients[i] = x; 
		}
	}
	
	// Does centered mod for integer
	public int centerMod(int x, int alpha) {

	    int r0 = x % alpha;
	    if (r0 > (alpha >> 1)) {
	        r0 -= alpha;
	        }
	    return r0;
	}
	
	// Does modulo m centered reduction for Poly
	public void centeredMod(int m) {
		Poly ans = new Poly(this.polyLength);
		for (int i=0; i < this.polyLength; i++) {
			ans.coefficients[i] = centerMod(this.coefficients[i], m);
		}
	}
	
	//Integer division of every coefficient of Poly
	public Poly div(int m) {
		Poly ans = new Poly(this.polyLength);
		for (int i = 0; i < this.polyLength; i++) {
			ans.coefficients[i] = this.coefficients[i] / m;
		}
		return ans;
	}

	
	// Random polynomial generation
	
	 //for matrix A 
	public static Poly randomPoly(byte[] rho, int nonce) {
		
		int buflen = Params.POLYUNIFORMNBLOCKS * Params.STREAM128BLOCKBYTES;
		byte[] buffer = new byte[buflen + 2];

		SHAKEDigest s = new SHAKEDigest(128);
		s.update(rho, 0, rho.length);

		byte[] non = new byte[2];
		non[0] = (byte) (nonce & 0xFF);
		non[1] = (byte) ((nonce >> 8) & 0xFF);
		s.update(non, 0, 2);
		s.doOutput(buffer, 0, buflen);
		

		Poly x = new Poly(Params.N);
		int counter = rej_uniform(x.coefficients, 0, Params.N, buffer, buflen);

		while (counter < Params.N) {
			int off = buflen % 3;
			for (int i = 0; i < off; i++)
				buffer[i] = buffer[buflen - off + i];
			s.doOutput(buffer, off, Params.STREAM128BLOCKBYTES);
			buflen = Params.STREAM128BLOCKBYTES + off;
			counter += rej_uniform(x.coefficients, counter, Params.N - counter, buffer, buflen);

		}
		return x;
	}
	
	//for secret vector s1 and s2
	public static Poly randomPoly(byte[] rho, int eta, int nonce) { 
		int etaNBlocks;
		if (eta == 2) {
			etaNBlocks = ((136 + Params.STREAM128BLOCKBYTES - 1) / Params.STREAM128BLOCKBYTES);
		} else if (eta == 4) {
			etaNBlocks = ((227 + Params.STREAM128BLOCKBYTES - 1) / Params.STREAM128BLOCKBYTES);
		} else {
			throw new IllegalArgumentException("Non-defined eta (secret sampling parameter): " + eta);
		}

		int ctr;
		SHAKEDigest s = new SHAKEDigest(128);
		s.update(rho, 0, rho.length);
		byte[] non = new byte[2];
		non[0] = (byte) (nonce & 0xFF);
		non[1] = (byte) ((nonce >> 8) & 0xFF);
		s.update(non, 0, 2);

		byte[] bb = new byte[etaNBlocks * Params.STREAM128BLOCKBYTES];
		s.doOutput(bb, 0, bb.length);

		Poly x = new Poly(Params.N);
		ctr = rej_eta(eta, x.coefficients, 0, Params.N, bb, bb.length);

		while (ctr < Params.N) {
			s.doOutput(bb, 0, Params.STREAM128BLOCKBYTES);
			ctr += rej_eta(eta, x.coefficients, ctr, Params.N - ctr, bb, Params.STREAM128BLOCKBYTES);

		}
		return x;

	}
	
	
	// Needed for beta in commitments
	public static Poly rangeUniform(int range){
		Poly res = new Poly();
		SecureRandom sRand = new SecureRandom();
		int ans = 0;
		for(int i=0; i<res.polyLength; i++){
			ans = sRand.nextInt(range + 1 + range) - range;
			res.coefficients[i] = ans;
		}
		return res;
	}
	
	//to generate y vector (session key)
	public static Poly randomPoly(byte[] seed,  int gamma1, int N, int nonce) { 
		Poly x = new Poly(N);
		byte[] buf = new byte[Params.POLYUNIFORMGAMMA1NBLOCKS * Params.STREAM256BLOCKBYTES];
		SHAKEDigest s = new SHAKEDigest(256);
		s.update(seed, 0, seed.length);

		byte[] non = new byte[2];
		non[0] = (byte) (nonce & 0xFF);
		non[1] = (byte) ((nonce >> 8) & 0xFF);
		s.update(non, 0, 2);
		s.doOutput(buf, 0, buf.length);

		if (gamma1 == (1 << 17)) {
			for (int i = 0; i < N / 4; i++) {
				x.coefficients[4 * i + 0] = (buf[9 * i + 0] & 0xFF);
				x.coefficients[4 * i + 0] |= (int) (buf[9 * i + 1] & 0xFF) << 8;
				x.coefficients[4 * i + 0] |= (int) (buf[9 * i + 2] & 0xFF) << 16;
				x.coefficients[4 * i + 0] &= 0x3FFFF;

				x.coefficients[4 * i + 1] = (buf[9 * i + 2] & 0xFF) >> 2;
				x.coefficients[4 * i + 1] |= (int) (buf[9 * i + 3] & 0xFF) << 6;
				x.coefficients[4 * i + 1] |= (int) (buf[9 * i + 4] & 0xFF) << 14;
				x.coefficients[4 * i + 1] &= 0x3FFFF;

				x.coefficients[4 * i + 2] = (buf[9 * i + 4] & 0xFF) >> 4;
				x.coefficients[4 * i + 2] |= (int) (buf[9 * i + 5] & 0xFF) << 4;
				x.coefficients[4 * i + 2] |= (int) (buf[9 * i + 6] & 0xFF) << 12;
				x.coefficients[4 * i + 2] &= 0x3FFFF;

				x.coefficients[4 * i + 3] = (buf[9 * i + 6] & 0xFF) >> 6;
				x.coefficients[4 * i + 3] |= (int) (buf[9 * i + 7] & 0xFF) << 2;
				x.coefficients[4 * i + 3] |= (int) (buf[9 * i + 8] & 0xFF) << 10;
				x.coefficients[4 * i + 3] &= 0x3FFFF;

				x.coefficients[4 * i + 0] = gamma1 - x.coefficients[4 * i + 0];
				x.coefficients[4 * i + 1] = gamma1 - x.coefficients[4 * i + 1];
				x.coefficients[4 * i + 2] = gamma1 - x.coefficients[4 * i + 2];
				x.coefficients[4 * i + 3] = gamma1 - x.coefficients[4 * i + 3];
				} 
			} else if (gamma1 == (1 << 19)) {
				for (int i = 0; i < N / 2; i++) {
					x.coefficients[2 * i + 0] = buf[5 * i + 0] & 0xFF;
					x.coefficients[2 * i + 0] |= (buf[5 * i + 1] & 0xFF) << 8;
					x.coefficients[2 * i + 0] |= (buf[5 * i + 2] & 0xFF) << 16;
					x.coefficients[2 * i + 0] &= 0xFFFFF;

					x.coefficients[2 * i + 1] = (buf[5 * i + 2] & 0xFF) >> 4;
					x.coefficients[2 * i + 1] |= (buf[5 * i + 3] & 0xFF) << 4;
					x.coefficients[2 * i + 1] |= (buf[5 * i + 4] & 0xFF) << 12;
					x.coefficients[2 * i + 0] &= 0xFFFFF;

					x.coefficients[2 * i + 0] = gamma1 - x.coefficients[2 * i + 0];
					x.coefficients[2 * i + 1] = gamma1 - x.coefficients[2 * i + 1];
				}

		} else {
			throw new IllegalArgumentException("Invalid gamma1: " + gamma1);
		}
		return x;
	}
	
	private static int rej_uniform(int[] coef, int off, int len, byte[] buf, int buflen) {
		int ctr, pos;
		int t;

		ctr = pos = 0;
		while (ctr < len && pos + 3 <= buflen) {
			t = (buf[pos++] & 0xFF);
			t |= ((int) buf[pos++] & 0xFF) << 8;
			t |= ((int) buf[pos++] & 0xFF) << 16;
			t &= 0x7FFFFF;

			if (t < Params.Q)
				coef[off + ctr++] = t;
		}
		return ctr;
	}
	
	private static int rej_eta(int eta, int[] coef, int off, int len, byte[] buf, int buflen) {
		int ctr, pos;
		int t0, t1;
		ctr = pos = 0;
		if (eta == 2) {
			while (ctr < len && pos < buflen) {
				t0 = buf[pos] & 0x0F;
				t1 = (buf[pos++] >> 4) & 0x0F;
				if (t0 < 15) {
					t0 = t0 - (205 * t0 >>> 10) * 5;
					coef[off + ctr++] = 2 - t0;
				}
				if (t1 < 15 && ctr < len) {
					t1 = t1 - (205 * t1 >>> 10) * 5;
					coef[off + ctr++] = 2 - t1;
				}
			}
		} else {
			while (ctr < len && pos < buflen) {
				t0 = buf[pos] & 0x0F;
				t1 = (buf[pos++] >> 4) & 0x0F;
				if (t0 < 9)
					coef[off + ctr++] = 4 - t0;
				if (t1 < 9 && ctr < len)
					coef[off + ctr++] = 4 - t1;
			}
		}
		return ctr;
	}
	
	public static Poly zeroPolynomial() { //for identity matrix
		Poly x = new Poly(Params.N);
		for(int i=0; i<x.polyLength; i++) {
			x.coefficients[i] = 0;
		}
		return x;
	}
	
	public static Poly onePolynomial() { //for identity matrix
		Poly x = new Poly(Params.N);
		for(int i=0; i<x.polyLength; i++) {
			x.coefficients[i] = 0;
			if(i==0)
				x.coefficients[i] = 1;
		}
		return x;
	}
	
	
	// Multiplication	
	
	// Needed in ntt
	private static int reduce32(int a) {
		int buf;
		buf = (a + (1 << 22)) >> 23;
		buf = a - buf * Params.Q;
		return buf;
	}
	
	// Inplace reduction of all coefficients of polynomial to representative in [-6283009,6283007].
	
	public Poly reduce() {
		Poly reduced = new Poly(this.polyLength);
		for(int i=0; i<reduced.polyLength; i++) {
			reduced.coefficients[i] = reduce32(this.coefficients[i]);
		}
		
		return reduced;
	}
	
	/*
	Description: For finite field element a with -2^{31}Q <= a <= Q*2^31,
	*              compute t \equiv a*2^{-32} (mod Q) such that -Q < r < Q.
	*/

	static int montgomery_reduce(long a) {
		int t;

		t = (int) (a * Params.QINV);
		t = (int) (((a - ((long) t) * Params.Q) >> 32) & 0xFFFFFFFF);
		return t;
	}
	
	/*
	 * * Description: Computes negacyclic number-theoretic transform (NTT) of
	 *   a polynomial in place;
	 *   inputs assumed to be in normal order, output in bitreversed order
	 */
	
	public Poly pointwiseMontgomery (Poly x) {
		Poly ans = new Poly(x.polyLength);
		for (int i = 0; i < ans.polyLength; i++) {
			ans.coefficients[i] = montgomery_reduce(((long) (this.coefficients[i])) * x.coefficients[i]);
		}
		return ans;

	}
	
	/*
	* Name:        ntt
	* Description: Forward NTT, in-place. No modular reduction is performed after
	*              additions or subtractions. Output vector is in bitreversed order.
	*/
	
	public Poly ntt() {
		int k=0, j=0, t=0;
		Poly ans = new Poly(this.polyLength);
		for(int i=0; i < this.polyLength; i++) {
			ans.coefficients[i] = this.coefficients[i];
		}
		for(int length=128; length > 0; length >>=1){
			for(int start = 0; start < this.polyLength; start = j + length) {
				int zeta = Params.zetas[++k];
				for (j = start; j < start + length; ++j) {
					t = montgomery_reduce((long) zeta * ans.coefficients[j + length]);
					ans.coefficients[j+length] = ans.coefficients[j] - t;
					ans.coefficients[j] = ans.coefficients[j] + t;
				}
			}
		}
		return ans;
	}
	
	/*
	* Name:        invntt_tomont
	* Description: Inverse NTT and multiplication by Montgomery factor 2^32.
	*              In-place. No modular reductions after additions or
	*              subtractions; input coefficients need to be smaller than
	*              Q in absolute value. Output coefficient are smaller than Q in
	*              absolute value.
	*/
	
	public void invnttTomont() {
		int j;
		final int f = 41978; // mont^2/256

		int k = Params.N; 
		for (int length = 1; length < Params.N; length <<= 1) {
			for (int start = 0; start < Params.N; start = j + length) {
				int zeta = -Params.zetas[--k];
				for (j = start; j < start + length; ++j) {
					int t = coefficients[j];
					coefficients[j] = t + coefficients[j + length];
					coefficients[j + length] = t - coefficients[j + length];
					coefficients[j + length] = montgomery_reduce(((long) zeta) * coefficients[j + length]);
				}
			}
		}

		for (j = 0; j < Params.N; ++j) {
			coefficients[j] = montgomery_reduce(((long) f) * coefficients[j]);
		}
	}
	
	/* Description: For finite field element a with a <= 2^{31} - 2^{22} - 1,
			*              compute r \equiv a (mod Q) such that -6283009 <= r <= 6283007.
	*/
	
	
	//HighBits
	public Poly[] decompose(final int gamma2, boolean m) { // hardcoded for Dilithium parameters
		Poly[] x = new Poly[2];
		x[0] = new Poly(Params.N);
		x[1] = new Poly(Params.N);

		for (int i = 0; i < this.coefficients.length; i++) {
			int a = this.coefficients[i];

			int a1 = (a + 127) >> 7;
		
		if (gamma2 == (Params.Q - 1) / 32) {
			a1 = (a1 * 1025 + (1 << 21)) >> 22;
			a1 &= 15;

		} else if (gamma2 == (Params.Q - 1) / 88) {
			a1 = (a1 * 11275 + (1 << 23)) >> 24;
			a1 ^= ((43 - a1) >> 31) & a1;
		} 
		else {
			throw new IllegalArgumentException("Invalid gamma2: " + gamma2);
		}
		x[0].coefficients[i] = a - a1 * 2 * gamma2;
		x[0].coefficients[i] -= (((Params.Q - 1) / 2 - x[0].coefficients[i]) >> 31) & Params.Q;
		x[1].coefficients[i] = a1;
		}
		return x;
	}
	
	public Poly[] decompose(int gamma2) { // outputs for any possible parameters
		Poly[] x = new Poly[2];
		x[0] = new Poly(Params.N);
		x[1] = new Poly(Params.N);

		for (int i = 0; i < this.coefficients.length; i++) {
			int r = this.coefficients[i];
			r = r % Params.Q;
			int r0 = centerMod(r, gamma2);
			int r1;
			
			if ((r - r0) == Params.Q-1) {
				r1 = 0;
				r0 = r0 - 1;
				x[0].coefficients[i] = r0;
				x[1].coefficients[i] = r1;
			}
			else {
				r1 = (int) (r-r0) / gamma2;
				x[0].coefficients[i] = r0;
				x[1].coefficients[i] = r1; 
			}
		
		}
		return x;
	}
	
	//Rejection sampling
	public boolean checkNorm(int bound) {
		int t;

		if (bound > (Params.Q - 1) / 8)
			return true;

		/*
		 * It is ok to leak which coefficient violates the bound since the probability
		 * for each coefficient is independent of secret data but we must not leak the
		 * sign of the centralized representative.
		 */
		for (int i = 0; i < Params.N; i++) {
			/* Absolute value */
			t = this.coefficients[i] >> 31;
		t = this.coefficients[i] - (t & 2 * this.coefficients[i]);

		if (t >= bound) {
			return true;
			}
		}

		return false;

	}
	
	public static Poly challenge(int tau, byte[] seed) {
		Poly ans = new Poly(Params.N);
		int b, pos;
		long signs;
		byte[] buf = new byte[Params.SHAKE256RATE];

		SHAKEDigest s = new SHAKEDigest(256);
		s.update(seed, 0, Params.SEEDBYTES);
		s.doOutput(buf, 0, buf.length);

		signs = 0;
		for (int i = 0; i < 8; i++)
			signs |= (long) (buf[i] & 0xFF) << 8 * i;
		pos = 8;

		for (int i = Params.N - tau; i < Params.N; ++i) {
			do {
				if (pos >= Params.SHAKE256RATE) {
					s.doOutput(buf, 0, buf.length);
					pos = 0;
				}

				b = (buf[pos++] & 0xFF);
			} while (b > i);
			ans.coefficients[i] = ans.coefficients[b];
			ans.coefficients[b] = (int) (1 - 2 * (signs & 1));
			signs >>= 1;
		}
		return ans;
	}
	
	public boolean equals(Poly a) {
		if (this.polyLength != a.polyLength)
			return false;
		if (!Arrays.equals(this.coefficients, a.coefficients))
			return false;
		return true;
	}
	
	public Poly cMod(int m) {
		Poly ans = new Poly(this.polyLength);
		for (int i=0; i < this.polyLength; i++) {
			ans.coefficients[i] = centerMod(this.coefficients[i], m);
		}
		return ans;
	}

	@Override
	public String toString(){
		return Arrays.toString(this.coefficients);
	}
	

}

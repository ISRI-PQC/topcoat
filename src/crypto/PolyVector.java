package crypto;

import java.io.Serializable;
import java.util.Arrays;


public class PolyVector implements Serializable {
	
	//Constructors 
	
	private static final long serialVersionUID = 6873920590593695677L;
	public Poly[] polynomial; 
	public int length; 
	
	public PolyVector(int length)
	{
		this.length = length; 
		this.polynomial = new Poly[length];
	}
	
	public PolyVector(Poly[] a, int length)
	{
		this.length = length; 
		this.polynomial = a;
	}
	
	// Random generation
	// Needed for s1 and s2
	public static PolyVector secret(byte[] rho, int eta, int length, int nonce) {
		PolyVector r = new PolyVector(length);
		for (int i=0; i<length; i++) {
			r.polynomial[i] = Poly.randomPoly(rho, eta, nonce);
		}
		return r;
	}
	
	// To generate matrix from seed
	public static PolyVector[] expandA(byte[] rho, int k, int l) {
		PolyVector[] A = new PolyVector[k];
		for(int i=0; i < k; i++) {
			A[i] = new PolyVector(l);
			for(int j=0; j < l; j++) {
				A[i].polynomial[j] = Poly.randomPoly(rho, (i << 8) + j);
			}
		}
		return A;
	}
	//To generate y
	public static PolyVector sessionKey(byte[] seed, int gamma1, int length, int nonce) {
		PolyVector r = new PolyVector(length);
		for (int i=0; i<length; i++) {
			r.polynomial[i] = Poly.randomPoly(seed, gamma1, Params.N, length * nonce + i);
		}
		return r;
	}
	//Needed for commitment matrices A1 and A2
	public static PolyVector[] identityMatrix(int k, int l) {
		PolyVector[] A = new PolyVector[k];
		for(int i=0; i < k; i++) {
			A[i] = new PolyVector(l);
			for(int j=0; j < l; j++) {
				if (j==i)
					A[i].polynomial[j] = Poly.onePolynomial();
				else 
					A[i].polynomial[j] = Poly.zeroPolynomial();
			}
		}
		return A;
	}
	
	//Addition for matricies
	public static PolyVector[] add(PolyVector[] a, PolyVector[] b) {
		PolyVector[] A = new PolyVector[Params.K]; 
		for(int i=0; i < Params.K; i++) {
			A[i] = new PolyVector(Params.L);
			for(int j=0; j<Params.L; j++) {
				A[i].polynomial[j] = a[i].polynomial[j].add(b[i].polynomial[j]);
			}
		}
		return A;
	}
	//Addition for vectors
	public PolyVector add(PolyVector a) {
		PolyVector ans = new PolyVector(this.length); 
		for(int i=0; i < ans.length; i++) {
			ans.polynomial[i] = this.polynomial[i].add(a.polynomial[i]);
		}
		return ans;
	}
	//Subtraction for vectors
	public PolyVector subtract(PolyVector a) {
		PolyVector ans = new PolyVector(this.length); 
		for(int i=0; i < ans.length; i++) {
			ans.polynomial[i] = this.polynomial[i].sub(a.polynomial[i]);
		}
		return ans;
	}
	
	
	public PolyVector multiplyByConst(int c) {
		PolyVector ans = new PolyVector(this.length); 
		for(int i=0; i < ans.length; i++) {
			ans.polynomial[i] = this.polynomial[i].multiplyByConst(c);
		}
		return ans;
	}
	
	
	public void caddq() {
		for(int i=0; i<this.length; i++) {
			 this.polynomial[i].caddq();
		}
	}
	
	public void mod(int m) {
		for(int i=0; i<this.length; i++) {
			 this.polynomial[i].mod(m);
		}
	}
	
	public PolyVector cMod(int m) {
		PolyVector ans = new PolyVector(this.length);
		for(int i=0; i<this.length; i++) {
			ans.polynomial[i] = this.polynomial[i].cMod(m);
		}
		return ans;
	}
	
	public PolyVector divide(int m) {
		PolyVector ans = new PolyVector(this.length); 
		for(int i=0; i < ans.length; i++) {
			ans.polynomial[i] = this.polynomial[i].div(m);
		}
		return ans;
	}

	
	//NTT algebra and multiplication
	
	public PolyVector ntt() {
		PolyVector a = new PolyVector(this.length);
		for(int i=0; i<this.length; i++) {
			a.polynomial[i] = this.polynomial[i].ntt();
		}
		return a;
	}
	
	public void invnttTomont() {
		for(int i=0; i<this.length; i++) {
			 this.polynomial[i].invnttTomont();
		}
	}
	
	// Multiplication 
	public Poly vecPointwiseMontgomery(PolyVector a, PolyVector b) {
		Poly ans = a.polynomial[0].pointwiseMontgomery(b.polynomial[0]);
		for (int i=1; i < b.length; i++) {
			Poly buff = a.polynomial[i].pointwiseMontgomery(b.polynomial[0]);
			ans = ans.add(buff);
			//ans.mod(Params.Q); // double check
		}
		return ans;
	}

	
	public PolyVector matrixPointwiseMontgomery(PolyVector[] X) {
		PolyVector a = new PolyVector(X.length);
		for (int i=0; i < X.length; i++) {
			a.polynomial[i] = vecPointwiseMontgomery(X[i], this);
		}
		return a;
	}
	
	public PolyVector pointwiseMontgomery(Poly u) {
	    PolyVector r = new PolyVector(this.length);
	    for (int i = 0; i < this.polynomial.length; i++) {
	        r.polynomial[i] = u.pointwiseMontgomery(this.polynomial[i]);
	    }
	    return r;
	}
	
	
	
	public PolyVector reduce() {
		PolyVector a = new PolyVector(this.length);
		for(int i=0; i<this.length; i++) {
			a.polynomial[i] = this.polynomial[i].reduce();
		}
		return a;
	}
	
	// HighBits
	
	public PolyVector[] decompose() { //for 2*gamma2 , therefore for signature share
		PolyVector[] res = new PolyVector[2];
		res[0] = new PolyVector(this.length);
		res[1] = new PolyVector(this.length);
		for (int i = 0; i < this.length; i++) {
			Poly[] r = this.polynomial[i].decompose(Params.GAMMA2, true);
			res[0].polynomial[i] = r[0];
			res[1].polynomial[i] = r[1];
		}
		return res;
	}
	
	public PolyVector[] decompose(final int gamma2) { //for any gamma2 
		PolyVector[] res = new PolyVector[2];
		res[0] = new PolyVector(this.length);
		res[1] = new PolyVector(this.length);
		for (int i = 0; i < this.length; i++) {
			Poly[] r = this.polynomial[i].decompose(gamma2);
			res[0].polynomial[i] = r[0]; //lowbits
			res[1].polynomial[i] = r[1]; //highbits
		}
		return res;
	}
	
	public boolean checkNorm(int bound) {	
		for(Poly p : this.polynomial) {
			if (p.checkNorm(bound)) {
				return true;
			}
		}
		return false;
	}
	
	public boolean equals(PolyVector a) {
		
		if(a.length != this.length)
			return false;
		
		for(int i=0; i<this.length; i++) {
			if (!this.polynomial[i].equals(a.polynomial[i]))
				return false;
		}
		return true;
	}
	
	@Override
	public String toString(){
		String result = "";
		for(int i=0; i<this.length; i++)
			result += Arrays.toString(this.polynomial[i].coefficients) + " \n";
		return result; 
	}
	
	

}

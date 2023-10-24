package crypto.comm;


import crypto.Params;
import crypto.Poly;
import crypto.PolyVector;

public class Commitment {
	
	public final static int qCOMM = 8380417;
	public final static int NCOMM = 256;
	public final static int lCOMM = Params.K;
	public final static int nCOMM = 5;
	public final static int kCOMM = 15;
	public final static int D = 2;
	
	public final static int betaCOMM = 256;
	
	public PolyVector[] A1;
	public PolyVector[] A2;
	public PolyVector r;
	public PolyVector m;
	public PolyVector[] commitment;
	
	public Commitment(byte[] rho) {
		this.A1 = generateAOne(rho);
		this.A2 = generateATwo(rho);
	}
	
	public Commitment(PolyVector[] A1, PolyVector[] A2, PolyVector r, PolyVector m, PolyVector[] commitment) {
		this.A1 = A1;
		this.A2 = A2;
		this.r = r;
		this.m = m;
		this.commitment = commitment;
	}
	public PolyVector[] getC() {
		return this.commitment;
	}
	
	public PolyVector getC1() {
		return this.commitment[0];
	}
	
	public PolyVector getC2() {
		return this.commitment[1];
	}
	
	public PolyVector getR() {
		return this.r;
	}
	
	public static PolyVector[] generateAOne(byte[] rho) {
		PolyVector[] A1 = new PolyVector[nCOMM];
		for(int i=0; i< nCOMM; i++) {
			A1[i] = new PolyVector(kCOMM);
			for(int j=0; j < kCOMM; j++) {
				if(j<nCOMM) {
					if(j==i) 
						A1[i].polynomial[j] = Poly.onePolynomial();

					else 
						A1[i].polynomial[j] = Poly.zeroPolynomial();
				}
				 else A1[i].polynomial[j] = Poly.randomPoly(rho, (i << 8) + j);
					
			}
		}
		return A1;
	}
	
	public static PolyVector[] generateATwo(byte[] rho) {
		PolyVector[] A2 = new PolyVector[lCOMM];
		for(int i=0;  i < lCOMM; i++) {
			A2[i] = new PolyVector(kCOMM);
			for(int j = 0; j < kCOMM; j++) {
				if(j < (nCOMM + lCOMM)) {
					if(i==(j-nCOMM) && j >= nCOMM ) 
						A2[i].polynomial[j] = Poly.onePolynomial();

					else 
						A2[i].polynomial[j] = Poly.zeroPolynomial();
				} 
				else A2[i].polynomial[j] = Poly.randomPoly(rho, (i << 8) + j);
					
			}
		}
		return A2;
	}
	
	public static PolyVector generateR() {
		PolyVector r = new PolyVector(kCOMM);
		for (int j = 0; j < kCOMM; j++) {
			r.polynomial[j] = Poly.rangeUniform(betaCOMM);
		}
		
		return r;
	}
	
	public static PolyVector[] commit(PolyVector[] A1, PolyVector[] A2, PolyVector r, PolyVector x) {
		
		PolyVector rPrime = r.ntt();
		PolyVector c1 = rPrime.matrixPointwiseMontgomery(A1); 
		PolyVector c2 = rPrime.matrixPointwiseMontgomery(A2);
		c1 = c1.reduce();
		c2 = c2.reduce();
		c1.invnttTomont();
		c2.invnttTomont();
		
		c2 = c2.add(x);
		c1.mod(qCOMM);
		c2.mod(qCOMM);
		
		PolyVector comm[] = new PolyVector[2];
		comm[0] = c1;
		comm[1] = c2;
		
		return comm;
	}
	
	public static boolean open(PolyVector[] A1, PolyVector[] A2, PolyVector r, PolyVector x, PolyVector[] comm) {
		
		PolyVector check[] = commit(A1, A2, r, x);
		
		if (!check[1].equals(comm[1]) || !check[0].equals(comm[0]))
			return false;
		return true;
	}
	
	public static PolyVector[] addComm(PolyVector[] comm1, PolyVector[] comm2) {
		PolyVector comm[] = new PolyVector[2];
		comm[0] = comm1[0].add(comm2[0]);
		comm[1] = comm1[1].add(comm2[1]);
		
		comm[0].mod(Params.Q);
		comm[1].mod(Params.Q);
		
		return comm;
	}

}

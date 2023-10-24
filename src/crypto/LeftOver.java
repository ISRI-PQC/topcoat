package crypto;

import java.io.IOException;
import java.security.SecureRandom;

import crypto.comm.Commitment;
import interfaces.DiliziumTotalPrivateKey;

public class LeftOver {
	
	public Poly add(Poly a, Poly b) {
		if (a.polyLength != b.polyLength) {
			System.out.println("Polynomials must be of the same size!"); //TODO - transform into new type of exception
			throw new ArrayIndexOutOfBoundsException();
		}
		Poly c = new Poly(a.polyLength);

		for(int i=0; i < a.polyLength; i++) {
			c.coefficients[i] = (a.coefficients[i] + b.coefficients[i]) % Params.Q;
		}
		return c;
	}
	
	public Poly subtract(Poly a, Poly b) {
		if(a.polyLength != b.polyLength){
			System.out.println("Polynomials must be of the same size!"); //TODO - transform into new type of exception
			throw new ArrayIndexOutOfBoundsException();
		}
		Poly c = new Poly(a.polyLength);
		for(int i=0; i < a.polyLength; i++) {
			c.coefficients[i] = Math.floorMod((a.coefficients[i]- b.coefficients[i]), Params.Q);
		}
		return c;
	}
	
	public static Poly uniformPoly(){
		Poly res = new Poly();
		SecureRandom sRand = new SecureRandom();
		for(int i=0; i<res.polyLength; i++){
			res.coefficients[i]=sRand.nextInt(Params.Q);
		}
		return res;
	}
	
	public static Poly uniformPoly(int range){
		Poly res = new Poly();
		SecureRandom sRand = new SecureRandom();
		int ans = 0;
		for(int i=0; i<res.polyLength; i++){
			ans = sRand.nextInt(range + 1 + range) - range;
			res.coefficients[i] = ans;
		}
		return res;
	}
	
	public static PolyVector randomVector(int length, int range) {
		PolyVector r = new PolyVector(length);
		for (int i=0; i<length; i++) {
			SecureRandom random = new SecureRandom();
			byte[] seed = new byte[32];
			
			random.nextBytes(seed);
			r.polynomial[i] = Poly.randomPoly(seed, range, i);
		}
		return r;
	}
	
	public static void garbage() {
		byte[] rho = new byte[32];
		PolyVector[] A1 = Commitment.generateAOne(rho);
		PolyVector[] A2 = Commitment.generateATwo(rho);
		
		PolyVector r = Commitment.generateR();
		
		
		for(int i=0; i< Commitment.lCOMM; i++) {
			for(int j=0; j < Commitment.kCOMM; j++) {
				if(j == Commitment.kCOMM-1)
					System.out.println(A1[i].polynomial[j] + " ");
				else
					System.out.print(A1[i].polynomial[j]);
			}
		}
		
		System.out.println("--------------------------------");
		
		for(int i=0; i< Commitment.kCOMM; i++) {
			if(i == Commitment.kCOMM-1)
				System.out.println(r.polynomial[i] + " ");
				else
					System.out.print(r.polynomial[i]);
		}
		
		PolyVector rPrime = r.ntt();
		PolyVector c1 = rPrime.matrixPointwiseMontgomery(A1);
		PolyVector c2 = rPrime.matrixPointwiseMontgomery(A2);
		c1.reduce();
		c1.invnttTomont();
		
		for(int i=0; i< Commitment.lCOMM; i++) {
			if(i == Commitment.lCOMM-1)
				System.out.println(c1.polynomial[i] + " ");
				else
					System.out.print(c1.polynomial[i]);
		}
	}
	/*
public static Dilizium sign(DiliziumTotalPrivateKey sk, byte[] M) throws IOException {
		
		long start2 = System.currentTimeMillis();
		
		byte[] mu = Utils.crh(M);
		byte[] conc = Utils.concat(sk.getK(), mu);
		byte[] rhoPrime = Utils.crh(conc);
		
		
		
		SecureRandom random = new SecureRandom();
		byte[] seed = new byte[32];
		random.nextBytes(seed);	
		
		int kappa = 0;
		
		PolyVector[] A = sk.getA();
		PolyVector s1 = sk.getS1();
		PolyVector s2 = sk.getS2();
		
		byte[] h4 = hash(M, sk);
		Commitment cKeys = new Commitment(h4);
		PolyVector[] A1 = cKeys.A1;
		PolyVector[] A2 = cKeys.A2;
			
		s1 = s1.ntt();
		s2 = s2.ntt();
		
		PolyVector z;
		Poly challenge;
		
		PolyVector[] comm;
		
		
		while (true) {
			
		PolyVector y =  sessionY(rhoPrime, kappa++);
		PolyVector w = sessionW(A, y);
		PolyVector[] wHB = w.decompose();
		
		PolyVector r = Commitment.generateR();
		
		comm = Commitment.commit(A1, A2, r, wHB[1]);
		
		challenge = hash(mu, comm);
		
		Poly challengePrime = challenge.ntt();
		z = s1.pointwiseMontgomery(challengePrime);
		
		z.invnttTomont();
		z = z.add(y);
		z = z.reduce();
		
		if (z.checkNorm(Params.GAMMA1 - Params.BETA)) {
			System.out.println("It failed on Gamma1 - Beta condition");
			continue;
			}
		
		
		PolyVector lbCheck = s2.pointwiseMontgomery(challengePrime);
		lbCheck.invnttTomont();
		lbCheck = w.subtract(lbCheck);
		lbCheck = lbCheck.reduce();
		lbCheck.caddq();
		
		PolyVector check2[] = lbCheck.decompose();
		
		if (check2[0].checkNorm(Params.GAMMA2 - Params.BETA)) {
			System.out.println("It failed on Gamma2 - Beta condition");
			continue;
			}
		
		break;
		
		}
		
		long end2 = System.currentTimeMillis();  
		
		System.out.println("Elapsed Time in milli seconds: "+ (end2-start2));
		System.out.println("Success");
		Dilizium share = new Dilizium(z, comm, challenge);
		
		return share;
	}*/

}

/*		PolyVector comm[] = Commitment.commit(A1, A2, r, w1[1]);
		PolyVector comm1[] = Commitment.commit(A1, A2, r, w1[1]);
		PolyVector commResult[] = Commitment.addComm(comm, comm1);
		PolyVector a = new PolyVector(Params.K);
		a = w1[1].add(w1[1]);
		PolyVector rTot = r.add(r);
		PolyVector commCheck[] = Commitment.commit(A1, A2, rTot, a);
		
		System.out.println(Commitment.open(A1, A2, rTot, a, commResult));
		System.out.println(Commitment.open(A1, A2, r, w1[1], comm1));
		System.out.println(Commitment.open(A1, A2, r, w1[1], comm));
		
		System.out.println(a.polynomial[0]);
		System.out.println(w1[1].polynomial[0]);
		
		System.out.println(commResult[1].polynomial[0]);
		System.out.println(commCheck[1].polynomial[0]);
		
		System.out.println(w1);
		
		*
		PolyVector y1 =  sessionY(rhoPrime, kappa);
		PolyVector y2 =  sessionY(seed, kappa+9);
		
		PolyVector w1 = sessionW(A, y1);
		PolyVector w2 = sessionW(A, y2);
		
		
		PolyVector w1HB[] = w1.decompose();
		PolyVector w2HB[] = w2.decompose();
		
		PolyVector wHB = w1HB[1].add(w2HB[1]);
		PolyVector w = w1.add(w2);
		w.modQ();
		PolyVector[] wTest = w.decompose(2*Params.GAMMA2);
		PolyVector difference = wHB.subtract(wTest[1]);
		PolyVector difference1 = difference.divide(43);
		PolyVector hint = difference.cMod(22);
		
		PolyVector love = difference1.multiplyByConst(44);
		love = love.add(hint);
		
		
		PolyVector x1 = difference.subtract(hint);
		PolyVector x2 = x1.divide(44);
		
		System.out.println("Hb(w1+w2) " + x2.polynomial[0]);
		System.out.println("Did overflow happen "+ difference1.polynomial[0]);
		System.out.println(x2.equals(difference1)); // поймать когда тут false
		
		/*
		
		System.out.println("HighBits of w1 " + w1HB[1].polynomial[0]);
		System.out.println("HighBits of w2 " + w2HB[1].polynomial[0]);
		System.out.println("Hb(w1)+Hb(w2) " + wHB.polynomial[0]);
		System.out.println("Hb(w1+w2) " + wTest[1].polynomial[0]);
		System.out.println("Difference "+ minus.polynomial[0]);
		System.out.println("Did overflow happen "+ minusPrime.polynomial[0]);
		System.out.println("Hint "+ hint.polynomial[0]);
		
		System.out.println("FINAL "+ love.polynomial[0]);
		System.out.println(love.equals(minus));
		
		
			public static Dilizium addShares(Dilizium share1, Dilizium share2) throws Exception {
		PolyVector zTotal = share1.z.add(share2.z);
		zTotal.caddq();
		PolyVector[] commTotal = Commitment.addComm(share1.commitment, share2.commitment);
		
		if(share1.challenge != share2.challenge) {
			throw new Exception("Hashes are not equal");
		}
		
		Dilizium total = new Dilizium(zTotal, commTotal, share1.challenge);
		
		return total;
	}
		
		*/
		//minus.cMod(44);
		
		//System.out.println("Difference after 44 "+ minus.polynomial[0]);


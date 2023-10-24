//Mostly for single run

//Size = log(q)*N*l + log(q)*N*lcomm + log(q)*N*ncomm + log(q)*N*kcomm + N*k*2 + N*k*2 = 23×256×4 + 23×256×4 + 23×256×5 + 23×256×15+ 256×4×2 + 256×4×2
// Size = z + c1 + c2 +r + h1 + h2

package crypto;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.security.KeyPair;
import java.security.SecureRandom;

import org.bouncycastle.crypto.digests.SHAKEDigest;

import crypto.comm.Commitment;
import interfaces.DiliziumPrivateKey;
import interfaces.DiliziumPublicKey;
import interfaces.DiliziumTotalPrivateKey;
import interfaces.DiliziumTotalPublicKey;

public class Dilizium implements Serializable {
	
	private static final long serialVersionUID = 3460368757307242980L;
	public PolyVector z;
	public PolyVector[] commitment;
	public PolyVector rKey;
	public PolyVector[] hint;
	public PolyVector wHB;
	public int rejCount;
	
	public Dilizium(PolyVector z, PolyVector[] commitment, PolyVector rKey, PolyVector[] hint, PolyVector wHB, int rejCount) {
		this.z = z;
		this.commitment = commitment;
		this.rKey = rKey;
		this.hint = hint;
		this.wHB = wHB;
		this.rejCount = rejCount;
		
	}
	//Needed to generate commitment key ck in signing (look at step 1 of the algorithm) 
	
	public static Commitment genCommKeys(DiliziumTotalPrivateKey sk, byte[] M) throws IOException {
		PolyVector[] A = sk.getTotalA();
		PolyVector t = sk.getTotalT();
		byte[] h4 = Utils.hash4(M, A, t);
		Commitment cKeys = new Commitment(h4);
		
		return cKeys;
	}
	//Needed to generate commitment key ck in verification (look at step 1 of the algorithm) 
	public static Commitment genCommKeys(DiliziumTotalPublicKey pk, byte[] M) throws IOException {
		PolyVector[] A = pk.getTotalA();
		PolyVector t = pk.getTotalT();
		byte[] h4 = Utils.hash4(M, A, t);
		Commitment cKeys = new Commitment(h4);
		
		return cKeys;
	}
	
	public static PolyVector sessionY(byte[] rhoPrime, int kappa) {
		PolyVector y = PolyVector.sessionKey(rhoPrime, Params.GAMMA1, Params.L, kappa++);
		return y;
	}
	
	public static PolyVector sessionW(PolyVector[] A, PolyVector y) { 
		PolyVector yPrime = y.ntt();
		PolyVector w = yPrime.matrixPointwiseMontgomery(A);
		w = w.reduce();
		w.invnttTomont();
		w.caddq();
		w.mod(Params.Q);
		return w;
	}
	
	public static Commitment genCommShare(PolyVector w, PolyVector[] A, Commitment ck) {
		PolyVector[] wHB = w.decompose();
		PolyVector r = Commitment.generateR();
		PolyVector[] cArray = Commitment.commit(ck.A1, ck.A2, r, wHB[1]); //consists of c1 and c2
		Commitment comm = new Commitment(ck.A1, ck.A2, r, wHB[1], cArray);
		return comm;
	}
	

	public static boolean reject1(PolyVector z, String string, PolyVector s2, PolyVector w, Poly challengePrime) {
		s2 = s2.ntt();
		PolyVector lbCheck = s2.pointwiseMontgomery(challengePrime);
		lbCheck = lbCheck.reduce();
		lbCheck.invnttTomont();
		lbCheck = w.subtract(lbCheck);
		lbCheck.caddq();
		
		PolyVector check2[] = lbCheck.decompose();
		
		if (check2[0].checkNorm(Params.GAMMA2 - 2*Params.BETA)) {
			System.out.println("Signature from " + string + " rejected on conition Gamma2 - Beta");
			return true;
			}
		return false;
	}
	
	public static boolean rejectGamma1(PolyVector z) {
		if (z.checkNorm(Params.GAMMA1 - Params.BETA)) {
			return true;
		}
		return false;
	}
	
	public static boolean rejectGamma2(PolyVector z, PolyVector s2, PolyVector w, Poly challengePrime) {
		s2 = s2.ntt();
		PolyVector lbCheck = s2.pointwiseMontgomery(challengePrime);
		lbCheck = lbCheck.reduce();
		lbCheck.invnttTomont();
		lbCheck = w.subtract(lbCheck);
		lbCheck.caddq();
		lbCheck.mod(Params.Q);
		
		PolyVector check2[] = lbCheck.decompose();
		
		if (check2[0].checkNorm(Params.GAMMA2 - Params.BETA)) {
			return true;
			}
		return false;
	}
	
	public static PolyVector zShare(Poly challengePrime, PolyVector s1, PolyVector y){
		s1 = s1.ntt();
		PolyVector z = s1.pointwiseMontgomery(challengePrime);
		z.invnttTomont();
		z = z.reduce();
		z = z.add(y);
		
		return z;
	}
	
	public static PolyVector VerifyHB(PolyVector z, DiliziumTotalPrivateKey sk, Poly challengePrime, PolyVector t) {
		PolyVector[] A = sk.getTotalA();
		z = z.ntt();
		t = t.ntt(); // in mod +-
		PolyVector p1 = z.matrixPointwiseMontgomery(A);
		PolyVector p2 = t.pointwiseMontgomery(challengePrime);
		PolyVector w = p1.subtract(p2);
		//p1 = p1.reduce();
		//p2 = p2.reduce();
		//p1.invnttTomont();
		//p2.invnttTomont();
		w = w.reduce();
		w.invnttTomont();
		
		w.caddq();
		//w.mod(Params.Q);
		
		
		PolyVector[] wHB = w.decompose();

		
		return wHB[1];
	}
	
	
	
	public static Dilizium signTotal(DiliziumTotalPrivateKey sk1, DiliziumTotalPrivateKey sk2, byte[] M) throws IOException {
		//byte[] rhoPrime = Utils.crh(M);
		
		SecureRandom random1 = new SecureRandom();
		SecureRandom random2 = new SecureRandom();
		byte[] seed1 = new byte[32];
		byte[] seed2 = new byte[32];
		random1.nextBytes(seed1);
		random2.nextBytes(seed2);
		
		Commitment cKeys = genCommKeys(sk1, M);
		
		PolyVector[] A = sk1.getTotalA();

		PolyVector[] secretsClient = new PolyVector[] {sk1.getS1(), sk1.getS2()};
		PolyVector[] secretsServer = new PolyVector[] {sk2.getS1(), sk2.getS2()};
		
		int kappa1 = 0;
		int kappa2 = Params.K;
		
		PolyVector z;
		PolyVector r;
		Poly challenge;
		
		PolyVector[] comm;
		PolyVector[] HINT;
		PolyVector wHB;
		
		while (true) {
			PolyVector y1 = sessionY(seed1, kappa1++);
			PolyVector y2 = sessionY(seed2, kappa2++);
			PolyVector w1 = sessionW(A, y1);
			PolyVector w2 = sessionW(A, y2);
			
			Commitment comm1 = genCommShare(w1, A, cKeys);
			Commitment comm2 = genCommShare(w2, A, cKeys);
			
			PolyVector r1 = comm1.getR();
			PolyVector r2 = comm2.getR();
			
			//PUT HASHES CALCULATIONS!!!!
			
			comm = Commitment.addComm(comm1.getC(), comm2.getC());
			challenge = Utils.hash0(M, comm);
			Poly challengePrime = challenge.ntt();
			
			PolyVector z1 = zShare(challengePrime, secretsClient[0], y1);
			PolyVector z2 = zShare(challengePrime, secretsServer[0], y2);
			
			if(rejectGamma1(z1)) {
				System.out.println("Signature from Client rejected on conition GAMMA1 - Beta");
				continue;
			}
			if(rejectGamma1(z2)) {
				System.out.println("Signature from Server rejected on conition GAMMA1 - Beta");
				continue;
			}
			
			if(rejectGamma2(z1, secretsClient[1], w1, challengePrime)) {
				System.out.println("Signature from Client rejected on conition gamma2 - Beta");
				continue;
			}
			if(rejectGamma2(z2, secretsServer[1], w2, challengePrime)) {
				System.out.println("Signature from Server rejected on conition gamma2 - Beta");
				continue;
			}
			
			//PUT HASHES CALCULATIONS!!!!
			
			PolyVector wHB1 = comm1.m;
			PolyVector wHB2 = comm2.m;;
			
			//System.out.println(wHB1);
			
			PolyVector wHatHB = wHB1.add(wHB2);
			
			VerifyHB(z1, sk1, challengePrime, sk2.getOtherPartyT());
			
			r = r1.add(r2);
			r.mod(Params.Q);
			z = z1.add(z2);
			z.mod(Params.Q);
			PolyVector s = secretsClient[1].add(secretsServer[1]);
			PolyVector w = w1.add(w2);
			w.mod(Params.Q);
			
			
			if (reject1(z, "Total", s, w, challengePrime)) {
				
			}
			
			s = s.ntt();
			PolyVector cs = s.pointwiseMontgomery(challengePrime);
			cs = cs.reduce();
			cs.invnttTomont();
			w = w.subtract(cs);
			w.caddq();
			w.mod(Params.Q);
			
			PolyVector[] wComp = w.decompose();
			wHB = wComp[1];
			
			PolyVector h = wHB.subtract(wHatHB);
			PolyVector h1 = h.divide(43);
			PolyVector h2 = h;
			PolyVector h3 = h.cMod(22);
			h2.mod(44);
			h2 = h2.cMod(22);
			
			HINT = new PolyVector[] {h1, h2};
			
			
			/*
			System.out.println("Recalculated");
			for(int i=0; i<Params.L; i++) {
				System.out.println(wHB1.polynomial[i]);
			}
			
			System.out.println("original");
			for(int i=0; i<Params.L; i++) {
				System.out.println(comm1.m.polynomial[i]);
			}
			*/
			
			//System.out.println(z1.polynomial[0]);
		
			
			break;
			
		}
		
		return new Dilizium(z, comm, r, HINT, wHB, kappa1);
	}
	
	public static PolyVector UseHint(PolyVector r, PolyVector[] hint, int alpha) {
		PolyVector h = hint[0].multiplyByConst(alpha);
		h = h.add(hint[1]);
		r = r.subtract(h);
		return r;
	}
	
	public static boolean verifyTotal(DiliziumTotalPublicKey pk, byte[] M, Dilizium sigma) throws IOException {
		
		Commitment cKeys = genCommKeys(pk, M);
		Poly challenge = Utils.hash0(M, cKeys.getC());
		
		PolyVector wHB = sigma.wHB;
		
		PolyVector r = UseHint(wHB, sigma.hint, 44);
		
		boolean rej = sigma.z.checkNorm(2*(Params.GAMMA1 - Params.BETA));
		rej = false;
		return Commitment.open(cKeys.A1, cKeys.A2, sigma.rKey, r, sigma.commitment) && !rej;
	
	}
	
	
	
	
	

	
}

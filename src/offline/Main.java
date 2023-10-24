package offline;

import java.io.IOException;
import java.lang.Math;
import java.security.KeyPair;
import java.security.SecureRandom;
import org.bouncycastle.crypto.digests.SHAKEDigest;

import crypto.*;
import crypto.comm.Commitment;
import interfaces.DiliziumPrivateKey;
import interfaces.DiliziumPublicKey;
import interfaces.DiliziumTotalPrivateKey;
import interfaces.DiliziumTotalPublicKey;


public class Main {
	
	
	public static void main(String args[]) throws Exception {
		// t = As_1 + s_2
		
		// y - random
		// w = Ay 
		// hb= HB(w)
		// c = H(m||hb)
		// z = y +cs_1
		// Rejection
		
		
		SecureRandom random1 = new SecureRandom();
		SecureRandom random2 = new SecureRandom();
		byte[] seed1 = new byte[32];
		byte[] seed2 = new byte[32];
		random1.nextBytes(seed1);
		random2.nextBytes(seed2);
		
		
		
		System.out.println("Key Generation times");
		long keyGenTimeStart = System.currentTimeMillis();
		
		KeyPair kp1 = KeyGen.KeyShare(seed1);
		KeyPair kp2 = KeyGen.KeyShare(seed2);
		

		DiliziumPrivateKey sk1 = (DiliziumPrivateKey) kp1.getPrivate();
		DiliziumPrivateKey sk2 = (DiliziumPrivateKey) kp2.getPrivate();
		
		DiliziumPublicKey pk = (DiliziumPublicKey) kp1.getPublic();
		
		PolyVector Ac[] = sk1.getA(); 
		PolyVector As[] = sk2.getA();
		
		PolyVector t1 = sk1.getT(); 
		PolyVector t2 = sk2.getT();
		
		PolyVector A[] = KeyGen.totalA(Ac, As);
		PolyVector t = t1.add(t2);
		
		DiliziumTotalPrivateKey skTotal1 = new DiliziumTotalPrivateKey(sk1, A, t, t2);
		DiliziumTotalPrivateKey skTotal2 = new DiliziumTotalPrivateKey(sk2, A, t, t1);
		
		DiliziumTotalPublicKey pkTotal = new DiliziumTotalPublicKey(pk, A, t);
		
	
		
		/*
		for(int i=0; i<1000; i++) {
			
			random1.nextBytes(seed1);
			random1.nextBytes(seed2);
			
			kp1 = KeyGen.KeyG(seed1);
			kp2 = KeyGen.KeyG(seed2);
			
			sk1 = (DiliziumPrivateKey) kp1.getPrivate();
			sk2 = (DiliziumPrivateKey) kp2.getPrivate();
			pk = (DiliziumPublicKey) kp1.getPublic();
			
			Ac = sk1.getA(); 
			As = sk2.getA();
			
			t1 = sk1.getT(); 
			t2 = sk2.getT();
			
			A = KeyGen.totalA(Ac, As);
			t = t1.add(t2);
			
			skTotal1 = new DiliziumTotalPrivateKey(sk1, A, t, t2);
			skTotal2 = new DiliziumTotalPrivateKey(sk2, A, t, t1);
			
			pkTotal = new DiliziumTotalPublicKey(pk, A, t);
		}*/
		long keyGenTimeStartend = System.currentTimeMillis();  
		
		double result = (double) (keyGenTimeStartend-keyGenTimeStart) / 1000;
		
		System.out.println("Average KeyGen Elapsed Time in milli seconds: " + result);
		
		String inputString = "Hello, Estonia!";
		byte M[] =  inputString.getBytes();
		
		Dilizium sigma;
		System.out.println("It began....");
		long start2 = System.currentTimeMillis();
		int rejectTotal = 0;
		
		sigma = Dilizium.signTotal(skTotal1, skTotal2, M);
		rejectTotal += sigma.rejCount;
		for(int i=0; i<0; i++) {
			sigma = Dilizium.signTotal(skTotal1, skTotal2, M);
			rejectTotal += sigma.rejCount;
		}
		long end2 = System.currentTimeMillis();  
		
		result = (double) (end2-start2) / 1000;
		double resultReject = (double) rejectTotal / 1000;
		
		System.out.println("Average Signing Elapsed Time in milli seconds: " + result);	
		System.out.println("Average number of rejection " + resultReject);	
		
		//System.out.println(Dilizium.verifyTotal(pkTotal, M, sigma));
		
		long startVerif = System.currentTimeMillis();
				
		sigma = Dilizium.signTotal(skTotal1, skTotal2, M);
		for(int i=0; i<999; i++) {
			Dilizium.verifyTotal(pkTotal, M, sigma);
		}
		long endVerif = System.currentTimeMillis(); 
		
		result = (double) (endVerif-startVerif) / 1000;
		
		System.out.println("Average Vefication Elapsed Time in milli seconds: " + result);	



		
	}	
}

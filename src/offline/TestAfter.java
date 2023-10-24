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


public class TestAfter {
	
	public static void main(String args[]) throws Exception {
		SecureRandom random1 = new SecureRandom();
		SecureRandom random2 = new SecureRandom();
		byte[] seed1 = new byte[32];
		byte[] seed2 = new byte[32];
		random1.nextBytes(seed1);
		random2.nextBytes(seed2);
		
		KeyPair kp1 = KeyGen.KeyShare(seed1);
		KeyPair kp2 = KeyGen.KeyShare(seed2);
		
		KeyPair[] keys = KeyGen.KeyTotal(kp1, kp2);
		
		DiliziumTotalPrivateKey skTotal1 = (DiliziumTotalPrivateKey) keys[0].getPrivate();
		DiliziumTotalPrivateKey skTotal2 = (DiliziumTotalPrivateKey) keys[1].getPrivate();
		
		DiliziumTotalPublicKey pkTotal = (DiliziumTotalPublicKey) keys[0].getPublic();
		
		String inputString = "Hello, Estonia!";
		byte M[] =  inputString.getBytes();
		
		Dilizium sigma = Dilizium.signTotal(skTotal1, skTotal2, M);
		
		System.out.println(Dilizium.verifyTotal(pkTotal, M, sigma));
		
	}

}

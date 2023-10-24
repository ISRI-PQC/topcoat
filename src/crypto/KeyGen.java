package crypto;

import java.security.KeyPair;

import interfaces.DiliziumPrivateKey;
import interfaces.DiliziumPublicKey;
import interfaces.DiliziumTotalPrivateKey;
import interfaces.DiliziumTotalPublicKey;

public class KeyGen {
	
	public static PolyVector[] totalA(byte[] rho1, byte[] rho2) {
		PolyVector[] Aserver = PolyVector.expandA(rho1, Params.K, Params.L);
		PolyVector[] Aclient = PolyVector.expandA(rho2, Params.K, Params.L);
		PolyVector[] A = totalA(Aclient, Aserver);
		return A;
	}
	
	public static PolyVector[] totalA(PolyVector[] Aclient, PolyVector[] Aserver) {
		PolyVector[] A = PolyVector.add(Aclient, Aserver);
		return A;
	}
	
	public static PolyVector[] matrixA(byte[] rho) {
		PolyVector[] A = PolyVector.expandA(rho, Params.K, Params.L);
		return A;
	}
	
	public static PolyVector publicT(PolyVector[] A, PolyVector[] secrets) {
		PolyVector s1Prime = secrets[0].ntt(); 
		PolyVector t = s1Prime.matrixPointwiseMontgomery(A);
		t = t.reduce();
		t.invnttTomont();
		t = t.add(secrets[1]);
		t.caddq();
		
		return t;
	}
	
	public static PolyVector publicT(byte[] rho, byte[] rhoPrime) {
		PolyVector[] A = matrixA(rho);
		PolyVector[] secrets = secretKeys(rhoPrime);
		PolyVector t = publicT(A, secrets);
		return t;
	}
	
	
	public static PolyVector[] secretKeys(byte[] rhoPrime) {
		PolyVector secrets[] = new PolyVector[2];
		secrets[0] = PolyVector.secret(rhoPrime, Params.ETA, Params.L, 0);
		secrets[1] = PolyVector.secret(rhoPrime, Params.ETA, Params.K, Params.L);
		return secrets;
	}
	
	public static KeyPair KeyShare(byte[] seed) {
		
		byte[] zeta = seed; // 256 bit of randomness
		
		byte[] prgOutput = Utils.getSHAKE256Digest(5*32, zeta); // Extracting bytes using SHAKE-256
		byte[] rho = new byte[32]; 
		byte[] rhoPrime = new byte[32];
		byte[] K = new byte[32];
		
		System.arraycopy(prgOutput, 0, rho, 0, 32); // for matrix A
		System.arraycopy(prgOutput, 32, rhoPrime, 0, 32); // for secret keys
		System.arraycopy(prgOutput, 64, K, 0, 32); // for deterministic signing
		
		PolyVector[] A = matrixA(rho);
		PolyVector[] secrets = secretKeys(rhoPrime);
		PolyVector t = publicT(A, secrets);
		
		DiliziumPublicKey pk = new DiliziumPublicKey(rho, A, t);
		DiliziumPrivateKey sk = new DiliziumPrivateKey(rho, K, A, secrets[0], secrets[1], t);
		return new KeyPair(pk, sk);
	}
	
	public static KeyPair[] KeyTotal(KeyPair kp1, KeyPair kp2) {
		
		DiliziumPrivateKey sk1 = (DiliziumPrivateKey) kp1.getPrivate();
		DiliziumPrivateKey sk2 = (DiliziumPrivateKey) kp2.getPrivate();
		
		DiliziumPublicKey pk = (DiliziumPublicKey) kp1.getPublic();
		
		PolyVector Ac[] = sk1.getA(); 
		PolyVector As[] = sk2.getA();
		
		PolyVector t1 = sk1.getT(); 
		PolyVector t2 = sk2.getT();
		
		PolyVector A[] = KeyGen.totalA(Ac, As);
		PolyVector t = t1.add(t2);
		t.mod(Params.Q);
		
		DiliziumTotalPrivateKey skTotal1 = new DiliziumTotalPrivateKey(sk1, A, t, t2);
		DiliziumTotalPrivateKey skTotal2 = new DiliziumTotalPrivateKey(sk2, A, t, t1);
		
		DiliziumTotalPublicKey pkTotal = new DiliziumTotalPublicKey(pk, A, t);
		
		KeyPair client = new KeyPair(pkTotal, skTotal1);
		KeyPair server = new KeyPair(pkTotal, skTotal2);
		
		KeyPair[] keys = {client, server};
		
		return keys;
	}
}

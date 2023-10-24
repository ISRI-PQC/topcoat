package offline;

import java.security.SecureRandom;

import crypto.Params;
import crypto.Poly;

public class TestBrno {
	
	static int q = 8380417;
	static int d2 = 2048;
	
	public static void main(String args[]) throws Exception {
		
		/*
		 * Let's check if the principle works for at least one coefficient.
		 * If it does not, correctness does not hold. 
		 * */
		
		int t = 0; // Total key
		int tAlice = 0; // Alice's keyshare
		int tBob = 0; // Bob's keyshare
		int tCharlie = 0;
		/*
		 * To omit any "special" numbers, let's generate those share randomly 
		 */
		int count = 0;
		while(count < 10000000) {
		SecureRandom sRand = new SecureRandom();
		tAlice = sRand.nextInt(q+1); 
		tBob = sRand.nextInt(q+1); 
		tCharlie = sRand.nextInt(q+1); 
		
		//System.out.println(tAlice); 
		//System.out.println(tBob);
		//System.out.println(tCharlie);
		
		t = (tAlice + tBob + tCharlie); 
		t = Math.floorMod(t, q); // Shares added together modulo q
		
		//System.out.println(t);
		/*
		 * Following the protocol, let's calculate Power2Round separately for Alice's share and Bob's share 
		 */
		int[] powerA = Power2Round(tAlice);
		int[] powerB = Power2Round(tBob);
		int[] powerC = Power2Round(tCharlie);
 		
		/*
		 * During verification step key is recalculated using this formula
		 */
		int tPrime = (d2*(powerA[1] + powerB[1] + powerC[1]) + powerA[0] + powerB[0] + powerC[0]) ; // all calculations modulo q
		tPrime = Math.floorMod(tPrime, q);
		
		/*
		 * For double assurance, let's run Power2Round on original key and reconstruct it back.
		 */
		
		int[] power = Power2Round(t);
		int tReconstructed = d2*(power[1]) + power[0]; 
		
		
		//System.out.println("Actual key: " + t);
		//System.out.println("Reconstructed key: " + tReconstructed);
		//System.out.println("Two party key " + tPrime);
		
		if(t!=tReconstructed || t!=tPrime || tPrime!=tReconstructed) {
			System.out.println("Oh no, it is broken");
		}
		count++;
		}
		
		System.out.println("Oh no, it is actually works and Czechs are right");
		
		
	}
	
	// Implementation of Power2Rounf function. r[0] - represents r0, r[1] - represents r1 (https://pq-crystals.org/dilithium/data/dilithium-specification-round3-20210208.pdf)	
	public static int[] Power2Round(int x) {
		int[] r = new int[2];
		r[1] = (Math.floorMod(x, q)); 
		r[0] = centerMod(r[1], d2);
		r[1] = (r[1]-r[0]) / d2; 
		return r;
	}
	
	// Implementation of centeredMod function
	public static int centerMod(int x, int alpha) {
	    int r0 = Math.floorMod(x, alpha);
	    if (r0 > (alpha >> 1)) {
	        r0 -= alpha;
	        }
	    return r0;
	}

}

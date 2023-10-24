package crypto.comm;

import java.security.SecureRandom;
import java.util.concurrent.ThreadLocalRandom;

import org.bouncycastle.crypto.digests.SHAKEDigest;

import crypto.Params;
import crypto.Poly;

public class CommUtils {
	
	
	private static long rejUniformComQ(int[] coefficients, long counter, long l, byte[] buf, int buflen) {
		int ctr, pos;
		long t;
		int j = 0;
		ctr = pos = 0;
		while (ctr < l && pos + 3 <= buflen) {
		    t = buf[pos++];
		    for(j=8;j<64;j+=8)
		      t |= (long) buf[pos++] << j;
		    t &= (1L << 62)-1;

			if (t < Commitment.qCOMM)
				coefficients[(int) (counter + ctr++)] = (int) t;
		}
		return ctr;
	}
	
	
	public static Poly randomPolyCom(byte[] rho, int nonce) { //for matrix A1 and A2
		
		final int POLYCOMMUNIFORM = (4096*8 + Params.STREAM128BLOCKBYTES - 1) / Params.STREAM128BLOCKBYTES;
		
		int buflen = POLYCOMMUNIFORM * Params.STREAM128BLOCKBYTES;
		byte[] buffer = new byte[buflen + 2];

		SHAKEDigest s = new SHAKEDigest(256);
		s.update(rho, 0, rho.length);

		byte[] non = new byte[2];
		non[0] = (byte) (nonce & 0xFF);
		non[1] = (byte) ((nonce >> 8) & 0xFF);
		s.update(non, 0, 2);
		s.doOutput(buffer, 0, buflen);
		

		Poly x = new Poly(Params.N);
		long counter = rejUniformComQ(x.coefficients, 0, Params.N, buffer, buflen);
		
		

		while (counter < Params.N) {
			int off = buflen % 3;
			for (int i = 0; i < off; i++)
				buffer[i] = buffer[buflen - off + i];
			s.doOutput(buffer, off, Params.STREAM128BLOCKBYTES);
			buflen = Params.STREAM128BLOCKBYTES + off;
			counter += rejUniformComQ(x.coefficients, counter, Params.N - counter, buffer, buflen);

		}
		return x;
	}
	
	public static Poly randomPolyCom() {
		Poly res = new Poly();
		long ans = 0;
		for(int i=0; i<res.polyLength; i++){
			//ans = ThreadLocalRandom.current().nextLong(Commitment.qCOMM);
			ans = ThreadLocalRandom.current().nextLong(Commitment.qCOMM);
			res.coefficients[i] = (int) ans;
		}
		return res;
	}
	
	public static void paramCalc() {

		double x = (float) Commitment.nCOMM / Commitment.kCOMM;
		double y = (float) 1 / Commitment.kCOMM;
		double z = (float) -1 / (Commitment.kCOMM*2);
		double v = (float) 1/(Commitment.D);
		
		
		
		double dks1 = Math.pow(Commitment.qCOMM, x);
		double dks2 = Math.pow(2, y);
		
		double dks1Upper = 1/Math.sqrt(Commitment.D);
		double dks2Upper = Math.pow(Commitment.qCOMM, v);
		
		
		
		double sks1 = 3.871531;
		double sks2 = Math.pow(Commitment.qCOMM, x);
		double sks3 = Math.pow(2, z);
		
		
		System.out.println("DKS (2*betha should be bigger than this)");
		System.out.println(dks1*dks2);
		
		System.out.println("DKS (2*betha should be smaller than this)");
		System.out.println(dks1Upper*dks2Upper);
		
		System.out.println("SKS  (betha should be smaller than this)");
		System.out.println(sks1*sks2*sks3 - 8);
	}

}

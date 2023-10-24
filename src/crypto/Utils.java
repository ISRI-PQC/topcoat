package crypto;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;

import org.bouncycastle.crypto.digests.SHAKEDigest;

import interfaces.DiliziumTotalPrivateKey;



public class Utils {
	public static void clear(byte[] x)
	{
		for(int i = 0; i < x.length; i++) {
			x[i] = 0;
		}
	}

	public static byte[] concat(byte[]... arr) {
		ByteArrayOutputStream baos = new ByteArrayOutputStream();
		for (byte[] x : arr) {
			try {
				baos.write(x);
			} catch (IOException e) {
				throw new RuntimeException("Unexpected error");
			}
		}
		return baos.toByteArray();
	}

	public static byte[] getSHAKE256Digest(int sz, byte[]... arr) {
		byte[] c = concat(arr);
		SHAKEDigest s = new SHAKEDigest(256);
		s.update(c, 0, c.length);
		byte[] o = new byte[sz];
		s.doOutput(o, 0, o.length);
		return o;
	}

	static byte[] crh(byte[] p) {
		return getSHAKE256Digest(Params.CRHBYTES, p);
	}
	
	
	public static byte[] hash4(byte[] mu, PolyVector[] A, PolyVector t) throws IOException {
		
		byte[] ck = new byte[32];
		
		ByteArrayOutputStream baos = new ByteArrayOutputStream();
		ObjectOutputStream oos = new ObjectOutputStream(baos);
		oos.writeObject(A);
		oos.writeObject(t);
		byte[] keysBytes = baos.toByteArray();
		
		SHAKEDigest hash = new SHAKEDigest(256);
		hash.update(mu, 0, mu.length);
		hash.update(keysBytes, 0, keysBytes.length);
		hash.doOutput(ck, 0, 32);
		
		oos.close();
		baos.close();
		
		return ck;
	}
	
	public static Poly hash0(byte[] mu, PolyVector[] comm) throws IOException {
		
		byte[] cHat = new byte[32];
		
		ByteArrayOutputStream baos = new ByteArrayOutputStream();
		ObjectOutputStream oos = new ObjectOutputStream(baos);
		oos.writeObject(comm);
		byte[] commBytes = baos.toByteArray();
		
		SHAKEDigest hash = new SHAKEDigest(256);
		hash.update(mu, 0, mu.length);
		hash.update(commBytes, 0, commBytes.length);
		hash.doOutput(cHat, 0, 32);
		
		oos.close();
		baos.close();
		
		Poly challenge = Poly.challenge(Params.TAU, cHat);
		
		return challenge;
	}	
	
}

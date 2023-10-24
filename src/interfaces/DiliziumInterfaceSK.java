package interfaces;

import java.security.PrivateKey;

import crypto.PolyVector;

public interface DiliziumInterfaceSK extends PrivateKey {
	public byte[] getRho();
	public byte[] getK();
	public PolyVector getS1();
	public PolyVector getS2();
	public PolyVector getT();
	public PolyVector[] getA();

}

package interfaces;

import java.security.PublicKey;

import crypto.PolyVector;


public interface DiliziumInterfacePK extends PublicKey{
	
	public byte[] getRho();
	public PolyVector getT();
	public PolyVector[] getA();
	

}

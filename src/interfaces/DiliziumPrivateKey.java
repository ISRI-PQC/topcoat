package interfaces;

import crypto.PolyVector;

public class DiliziumPrivateKey implements DiliziumInterfaceSK {
	
	private static final long serialVersionUID = 1L;
	private final byte[] rho;
	private final byte[] K;
	private final PolyVector[] A;
	private final PolyVector s1;
	private final PolyVector s2;
	private final PolyVector t;


	
	public DiliziumPrivateKey(byte[] rho, byte[] K, PolyVector[] A, PolyVector s1, PolyVector s2, PolyVector t) {
		this.rho = rho;
		this.K = K;
		this.s1 = s1;
		this.s2 = s2;
		this.t = t;
		this.A = A;

	}
	
	@Override
	public String getAlgorithm() {
		return "Dilizium";
	}

	@Override
	public String getFormat() {
		return "RAW";
	}

	@Override
	public byte[] getEncoded() {
		return null;
	}

	@Override
	public byte[] getRho() {
		return rho;
	}

	@Override
	public byte[] getK() {
		return K;
	}

	@Override
	public PolyVector getS1() {
		return s1;
	}

	@Override
	public PolyVector getS2() {
		return s2;
	}
	
	@Override
	public PolyVector getT() {
		return t;
	}

	@Override
	public PolyVector[] getA() {
		return A;
	}

	

}

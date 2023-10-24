package interfaces;

import crypto.PolyVector;

public class DiliziumPublicKey implements DiliziumInterfacePK {
	
	//Key size  = rho + 3*log(q)*k*N= 256 + 3*23*256*4
	
	private static final long serialVersionUID = 1L;
	private final PolyVector t;
	private final byte[] rho;
	private final PolyVector[] A; 

	
	
	public DiliziumPublicKey(byte[] rho, PolyVector[] A, PolyVector t) {
		this.rho = rho;
		this.A = A;
		this.t = t;
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
	public PolyVector getT() {
		return t;
	}

	@Override
	public PolyVector[] getA() {
		return A;
	}


	

}

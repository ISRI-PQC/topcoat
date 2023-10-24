package interfaces;

import crypto.PolyVector;

public class DiliziumTotalPublicKey implements DiliziumTotalInterfacePK {
	
	private static final long serialVersionUID = 1L;
	private final PolyVector t;
	private final byte[] rho;
	private final PolyVector[] A; 
	private final PolyVector[] ATotal; 
	private final PolyVector tTotal; 
	
	
	public DiliziumTotalPublicKey(byte[] rho, PolyVector[] A, PolyVector t, PolyVector[] A1, PolyVector[] A2, PolyVector[] ATotal, PolyVector tTotal) {
		this.rho = rho;
		this.A = A;
		this.t = t;
		this.ATotal = ATotal;
		this.tTotal = tTotal;
	}
	
	public DiliziumTotalPublicKey(DiliziumPrivateKey sk, PolyVector[] ATotal, PolyVector tTotal) {
		this.rho = sk.getRho();
		this.A = sk.getA();
		this.t = sk.getT();
		this.ATotal = ATotal;
		this.tTotal = tTotal;
	}
	
	public DiliziumTotalPublicKey(DiliziumPublicKey pk, PolyVector[] ATotal, PolyVector tTotal) {
		this.rho = pk.getRho();
		this.A = pk.getA();
		this.t = pk.getT();
		this.ATotal = ATotal;
		this.tTotal = tTotal;
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

	@Override
	public PolyVector[] getTotalA() {
		return ATotal;
	}
	
	@Override
	public PolyVector getTotalT() {
		return tTotal;
	}
	
	

}

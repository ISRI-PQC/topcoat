package interfaces;

import crypto.PolyVector;

public class DiliziumTotalPrivateKey implements DiliziumTotalInterfaceSK {
	
	private static final long serialVersionUID = 1L;
	private final byte[] rho;
	private final byte[] K;
	private final PolyVector[] A;
	private final PolyVector s1;
	private final PolyVector s2;
	private final PolyVector t;
	private final PolyVector[] ATotal; 
	private final PolyVector tTotal; 
	private final PolyVector tOther;

	
	public DiliziumTotalPrivateKey(byte[] rho, byte[] K, PolyVector[] A, PolyVector s1, PolyVector s2, PolyVector t, PolyVector[] ATotal, PolyVector tTotal, PolyVector tOther) {
		this.rho = rho;
		this.K = K;
		this.s1 = s1;
		this.s2 = s2;
		this.t = t;
		this.A = A;
		this.ATotal = ATotal;
		this.tTotal = tTotal;
		this.tOther = tOther;
	}
	
	public DiliziumTotalPrivateKey(DiliziumPrivateKey sk, PolyVector[] ATotal, PolyVector tTotal, PolyVector tOther) {
		this.rho = sk.getRho();
		this.K = sk.getK();
		this.s1 = sk.getS1();
		this.s2 = sk.getS2();
		this.A = sk.getA();
		this.t = sk.getT();
		this.ATotal = ATotal;
		this.tTotal = tTotal;
		this.tOther = tOther;
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

	@Override
	public PolyVector[] getTotalA() {
		return ATotal;
	}
	
	@Override
	public PolyVector getTotalT() {
		return tTotal;
	}
	
	@Override
	public PolyVector getOtherPartyT() {
		return tOther;
	}

}

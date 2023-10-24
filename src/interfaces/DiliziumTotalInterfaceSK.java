package interfaces;

import crypto.PolyVector;

public interface DiliziumTotalInterfaceSK extends DiliziumInterfaceSK {
	
	public PolyVector getOtherPartyT();
	public PolyVector getTotalT();
	public PolyVector[] getTotalA();

}
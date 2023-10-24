package online;

import crypto.Params;

import java.security.Security;
import org.bouncycastle.jce.provider.BouncyCastleProvider;

public class Client {
	
	public static void main(String args[]) {
		int S = Params.ETA;
		
		Security.addProvider(new BouncyCastleProvider());
        if (Security.getProvider("BC") == null){
            System.out.println("Bouncy Castle provider is NOT available");
        }
        else{
            System.out.println("Bouncy Castle provider is available");
        }		
		System.out.println(S);
	}

}

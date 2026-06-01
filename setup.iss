; ============================================
; NetGer App Installer
; Created by: Joy Ravelo Tarigan
; Version: 1.2.0
; AppId: 23587c1c-3d5d-4dc1-98a0-3894b20b0f39
; ============================================

#define MyAppName "NetGer App"
#define MyAppVersion "1.2.0"
#define MyAppPublisher "Joy Ravelo Tarigan"
#define MyAppExeName "NetworkTools.exe"

[Setup]
AppId={{23587c1c-3d5d-4dc1-98a0-3894b20b0f39}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://www.linkedin.com/in/joy-ravelo/
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=output
OutputBaseFilename=NetGer_App_Setup_v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName} v{#MyAppVersion}
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Buat shortcut di Desktop"; GroupDescription: "Shortcut tambahan:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Jalankan {#MyAppName} sekarang"; Flags: nowait postinstall skipifsilent runascurrentuser

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('{#MyAppName} v{#MyAppVersion} berhasil diinstall!' + #13#10 + #13#10 +
           '✨ FITUR YANG TERSEDIA:' + #13#10 +
           '   • Firewall Command Generator' + #13#10 +
           '   • NSLookup Pro Tool (Multi-Thread)' + #13#10 +
           '   • Export hasil ke Excel' + #13#10 +
           '   • Support domain format [.]' + #13#10 +
           '📌 Shortcut Keyboard:' + #13#10 +
           '   • Ctrl+1 : Firewall Generator' + #13#10 +
           '   • Ctrl+2 : NSLookup Tool' + #13#10 +
           '👨‍💻 Created by Joy Ravelo Tarigan' + #13#10 +
           '🔗 LinkedIn: https://www.linkedin.com/in/joy-ravelo/',
           mbInformation, MB_OK);
  end;
end;
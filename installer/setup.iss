; Inno Setup Script — Legacy BJJ
; Gera: LegacyBJJ-{version}-windows-setup.exe

#define AppName      "Legacy BJJ"
#define AppPublisher "Legacy BJJ"
#define AppVersion   "1.0.0"
#define AppExe       "LegacyBJJ.exe"

[Setup]
AppId={{A7F3C2D1-4B8E-4F1A-9C2D-3E5F6A7B8C9D}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\LegacyBJJ
DefaultGroupName={#AppName}
OutputDir=dist
OutputBaseFilename=LegacyBJJ-{#AppVersion}-windows-setup
SetupIconFile=..\src\assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#AppExe}
MinVersion=10.0

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Ícones adicionais:"; Flags: checkedonce

[Files]
Source: "..\dist\LegacyBJJ\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}";        Filename: "{app}\{#AppExe}"; IconFilename: "{app}\{#AppExe}"
Name: "{group}\Desinstalar";       Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";  Filename: "{app}\{#AppExe}"; IconFilename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Iniciar {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

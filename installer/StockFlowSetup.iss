; StockFlow Per-User Windows Installer (Inno Setup 6)
; Builds a single Setup.exe with Start Menu shortcut, WebView2 check/install,
; in-place upgrades, and safe preservation of %APPDATA%\StockFlow user data.

#define MyAppName "StockFlow"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "StockFlow"
#define MyAppExeName "StockFlow.exe"

[Setup]
AppId={{8E9A7B2C-4F1D-4A3E-9C6B-1D2E3F4A5B6C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
UsePreviousAppDir=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist\installer
OutputBaseFilename=StockFlowSetup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\StockFlow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function IsWebView2Installed(): Boolean;
var
  Version: String;
begin
  Result := False;
  if RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) and (Version <> '') then
    Result := True
  else if RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) and (Version <> '') then
    Result := True
  else if RegQueryStringValue(HKCU, 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) and (Version <> '') then
    Result := True;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  SetupPath: String;
  ResultCode: Integer;
begin
  Result := '';
  if not IsWebView2Installed() then
  begin
    try
      SetupPath := ExpandConstant('{tmp}\MicrosoftEdgeWebview2Setup.exe');
      DownloadTemporaryFile('https://go.microsoft.com/fwlink/p/?LinkId=2124703', 'MicrosoftEdgeWebview2Setup.exe', '', nil);
      if FileExists(SetupPath) then
      begin
        if not Exec(SetupPath, '/silent /install', '', SW_SHOW, ewWaitUntilTerminated, ResultCode) then
          Result := 'Failed to run the Microsoft Edge WebView2 Runtime installer.';
      end;
    except
      Result := 'Microsoft Edge WebView2 Runtime is required and could not be downloaded. Please install WebView2 Runtime and re-run setup.';
    end;
  end;
end;

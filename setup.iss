[Setup]
AppName=Video Downloader
AppVersion=1.0
DefaultDirName={autopf}\Video Downloader
DefaultGroupName=Video Downloader
OutputDir=Output
OutputBaseFilename=Video_Downloader_Kurulum
Compression=lzma
SolidCompression=yes
SetupIconFile=compiler:Setup.ico

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; PyInstaller çıktısındaki tüm dosyaları kurulan dizine kopyalar
Source: "dist\Video Downloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Video Downloader"; Filename: "{app}\Video Downloader.exe"
Name: "{autodesktop}\Video Downloader"; Filename: "{app}\Video Downloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Video Downloader.exe"; Description: "{cm:LaunchProgram,Video Downloader}"; Flags: nowait postinstall skipifsilent
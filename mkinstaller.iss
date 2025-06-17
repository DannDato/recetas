[Setup]
AppName=Gestor de Recetas
AppVersion=1.0
AppPublisher=Alberto Daniel Tovar Mendoza
DefaultDirName={pf}\GestorRecetas
DefaultGroupName=Gestor de Recetas
OutputBaseFilename=recetas_installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "img\icono.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "img\receta.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "style\style.qss"; DestDir: "{app}\style"; Flags: ignoreversion
Source: "config.ini"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Gestor de Recetas"; Filename: "{app}\main.exe"

[Run]
Filename: "{app}\main.exe"; Description: "Iniciar Gestor de Recetas"; Flags: nowait postinstall skipifsilent

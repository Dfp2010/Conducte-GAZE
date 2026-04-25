' Lansează auto-push.ps1 silențios (fără fereastră CMD)
Dim shell
Set shell = CreateObject("WScript.Shell")
shell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & _
    CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & _
    "\auto-push.ps1""", 0, False
Set shell = Nothing

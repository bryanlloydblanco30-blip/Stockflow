Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strDir = fso.GetParentFolderName(WScript.ScriptFullName)

If fso.FileExists(strDir & "\dist\StockFlow\StockFlow.exe") Then
    WshShell.Run """" & strDir & "\dist\StockFlow\StockFlow.exe""", 0, False
Else
    WshShell.Run "python """ & strDir & "\desktop_app.py""", 0, False
End If

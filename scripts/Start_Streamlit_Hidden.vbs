Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this VBS file is located
strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Get the parent directory (project root)
strProjectDir = objFSO.GetParentFolderName(strScriptDir)

' Path to the virtual environment Python executable
strVenvPython = strProjectDir & "\venv\Scripts\python.exe"

' Path to the Python background launcher
strPythonFile = strProjectDir & "\tools\background_launcher.py"

' Create logs directory if it doesn't exist
strLogsDir = strScriptDir & "\logs"
If Not objFSO.FolderExists(strLogsDir) Then
    objFSO.CreateFolder(strLogsDir)
End If

' Check if virtual environment Python exists
If objFSO.FileExists(strVenvPython) And objFSO.FileExists(strPythonFile) Then
    ' Run the Python script completely hidden using virtual environment
    objShell.Run """" & strVenvPython & """ """ & strPythonFile & """", 0, False
Else
    ' Create error log if virtual environment or Python file not found
    Set objFile = objFSO.CreateTextFile(strLogsDir & "\startup_error.log", True)
    If Not objFSO.FileExists(strVenvPython) Then
        objFile.WriteLine Now & " - ERROR: Virtual environment Python not found: " & strVenvPython
    End If
    If Not objFSO.FileExists(strPythonFile) Then
        objFile.WriteLine Now & " - ERROR: Python launcher not found: " & strPythonFile
    End If
    objFile.Close
End If

Set objShell = Nothing
Set objFSO = Nothing

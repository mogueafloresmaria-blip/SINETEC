Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "c:\SINETEC\SINETEC"
WshShell.Run "cmd /c ""venv\Scripts\python.exe"" manage.py runserver 0.0.0.0:8000 --noreload", 0, False
MsgBox "¡Servidor SINETEC iniciado en segundo plano exitosamente!" & vbCrLf & vbCrLf & _
       "• En esta computadora:  http://localhost:8000" & vbCrLf & _
       "• En su celular (Wi-Fi): http://192.168.40.23:8000" & vbCrLf & vbCrLf & _
       "El servidor se ejecuta oculto sin ventanas. Ya puede cerrar todo en la PC.", _
       64, "SINETEC - Servidor Activo"

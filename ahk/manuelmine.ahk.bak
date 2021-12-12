;download Autohotkey unter: https://www.autohotkey.com/
;speichere unter filename.ahk (zb automine.ahk)

#SingleInstance Force
;#IfWinActive,"FiestaOnline"

while true 
	{	
		;suche nach dem gelb des klickbalkens
		PixelSearch, x, y, 914, 753, 1004, 757, 0xd6ffff, 0, Fast
		
		;wenn gefunden klicke ihn an
		if Not (x = None or y = None) 
		{	
			;verzögere den click leicht, sodass er registriert wird
			MouseClick, Left, x, y, 1, 0, D
			Sleep 50
			MouseClick, Left, x, y, 1, 0, U
			x = None
			y = None
			
			; clicke x (aufhebetaste) 4 mal
			; dafür unter aktionen aufsammeln in die taskbar legen und in den Einstellungen auf eine Taste festlegen
			loop 4 {
				send {x down}
				Sleep 50
				send {x up}
				Sleep 50
			}
			
			; warte eine halbe Sekunde
			Sleep 500
		}
	}


;tastenkombinastion zum beenden des scripts:
;gehen auch alle anderen kombis zb: ^y:: für strg + y
; alt + x
^p::
MsgBox, Exit
ExitApp
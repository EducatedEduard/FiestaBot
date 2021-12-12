#NoEnv
#SingleInstance force
#If WinActive("FiestaOnline")

$SPACE::

	While ( GetKeyState( "SPACE","P" ) ) {

		Send, {Space Down} 

		Sleep, 20
		Send, {Space Up} 
		Sleep, 20
		
	}

Return

$x::

	While ( GetKeyState( "X","P" ) ) {

		Send, {X Down} 

		Sleep, 20
		Send, {X Up} 
		Sleep, 20
		
	}

Return

#^0::
	Reload
#SingleInstance Force

while x = None and y = None
{	
	;if WinActive,"FiestaOnline"
	;{
		PixelSearch, x, y, 914, 753, 1004, 757, 0xd6ffff, 0, Fast
	;}
}

MouseClick, Left, x, y, 1, 0, D
Sleep 20
MouseClick, Left, x, y, 1, 0, U
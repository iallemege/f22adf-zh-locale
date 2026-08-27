# TCC stdcall exports _Name@N; the game imports undecorated DirectInput8Create.
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "DINPUT8.dll"
data = bytearray(open(path, "rb").read())
old = b"_DirectInput8Create@20\x00"
new = b"DirectInput8Create\x00@20\x00"
if old not in data:
    if b"DirectInput8Create\x00" in data:
        print("already undecorated")
        sys.exit(0)
    print("export string not found")
    sys.exit(1)
data = data.replace(old, new, 1)
open(path, "wb").write(data)
print("patched export name -> DirectInput8Create")

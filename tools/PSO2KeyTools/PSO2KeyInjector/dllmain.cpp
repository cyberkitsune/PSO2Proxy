#include <windows.h>
#include <stdio.h>
#if DUMPER
#include <string.h>
#endif

byte *RSAaddr = (byte *)0x33BDBE0;

#if DUMPER
void grabRSAKeysToFile()
{
	void* str = malloc(14); // SEGAKey#.blob\0
	int i;
	FILE* outFile;
	for (i = 0; i < 4; i++)
	{
		const void *ptr = (void*)(RSAaddr + (i * 0xA0)); // setup pointer
		sprintf(str, "SEGAKey%d.blob", i);
		fopen_s(&outFile, str, "wb"); // Write memory to disk
		fwrite(ptr, 0xA0, 1, outFile);
		fclose(outFile);
	}
}
#endif

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
	UNREFERENCED_PARAMETER(hinstDLL)
	UNREFERENCED_PARAMETER(lpvReserved)
	if (fdwReason == DLL_PROCESS_ATTACH)
	{
#if DUMPER
		grabRSAKeysToFile();
#else
		FILE* filePtr;
		int i;
		fopen_s(&filePtr, "publickey.blob", "rb");
		void* keyPtr = malloc(0xA0);
		fread(keyPtr, 0xA0, 1, filePtr);
		fclose(filePtr);
		
		for (i = 0; i < 4; i++)
		{
			memcpy((void*)(RSAaddr + (0xA0 * i)), keyPtr, 0xA0);
		}
#endif
	}

	return TRUE;
}

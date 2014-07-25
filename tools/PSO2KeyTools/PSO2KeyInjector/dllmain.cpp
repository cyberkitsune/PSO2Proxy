#include <Windows.h>
#include <stdio.h>
#if DUMPER
#include <string>
#endif

#if DUMPER
void grabRSAKeysToFile()
{
	void* ptr = malloc(0xA0);
	for (int i = 0; i < 4; i++)
	{
		memcpy(ptr, (void*)(0x33BDBE0 + (i * 0xA0)), 0xA0); // Copy key to memory
		FILE* outFile;
		fopen_s(&outFile, ("SEGAKey" + std::to_string(i) + ".blob").c_str(), "wb"); // Write memory to disk
		fwrite(ptr, 0xA0, 1, outFile);
		fclose(outFile);
	}
}
#endif

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
	if (fdwReason == DLL_PROCESS_ATTACH)
	{		
		#if DUMPER
		grabRSAKeysToFile();
		#else
		FILE* filePtr;
		fopen_s(&filePtr, "publickey.blob", "rb");
		void* keyPtr = malloc(0xA0);
		fread(keyPtr, 0xA0, 1, filePtr);
		fclose(filePtr);
		
		for (int i = 0; i < 4; i++)
		{
			memcpy((void*)(0x33BDBE0 + (0xA0 * i)), keyPtr, 0xA0);
		}
		#endif
	}

	return TRUE;
}
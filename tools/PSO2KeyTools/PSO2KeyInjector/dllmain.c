// Preprocessor related:

// Specify to the Windows API that we're not using all of it.
#define WIN32_LEAN_AND_MEAN

// Includes:

// Windows specific headers:
#include <windows.h>

// Standard C includes:
#include <stdio.h>
#include <stdlib.h>

// Constant variable(s):
const unsigned char* RSAaddr = (unsigned char*)0x33BDBE0;

// Functions:
#if DUMPER
	// Just in case we want to export this, I'm using 'VOID'.
	VOID grabRSAKeysToFile()
	{
		// At some point we may just want to put this on the stack.
		char* str = (char*)malloc(14); // SEGAKey#.blob\0

		FILE* outFile;
		
		/*
			This is for the loop, if we didn't care about C99 compatibility,
			we would have this in the 'for' loop.
		*/
		int i;

		for (i = 0; i < 4; i++)
		{
			// Setup the pointer.
			const void* ptr = (void*)(RSAaddr + (i * 0xA0));

			// Prepare the file name, then open the output file-stream:
			#if !defined(_CRT_SECURE_NO_WARNINGS) && defined(_MSC_VER)
				// This is just for the sake of shutting MSVC up:
				sprintf_s(str, 14, "SEGAKey%d.blob", i);
				fopen_s(&outFile, str, "wb");
			#else
				// Here's the standard C version:
				sprintf(str, "SEGAKey%d.blob", i);
				outFile = fopen(str, "wb");
			#endif
			
			// Write to the disk.
			fwrite(ptr, 0xA0, 1, outFile);
			
			// Close the output-file.
			fclose(outFile);
		}
		
		// Free the 'str' buffer.
		free(str);
		
		return;
	}
#endif

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
	UNREFERENCED_PARAMETER(hinstDLL);
	UNREFERENCED_PARAMETER(lpvReserved);
	
	if (fdwReason == DLL_PROCESS_ATTACH)
	{
		#if DUMPER
			grabRSAKeysToFile();
		#else
			FILE* filePtr;
			
			// Open the public-key file.
			#if !defined(_CRT_SECURE_NO_WARNINGS) && defined(_MSC_VER)
				fopen_s(&filePtr, "publickey.blob", "rb");
			#else
				filePtr = fopen("publickey.blob", "rb");
			#endif
			
			// Allocate the key.
			void* keyPtr = malloc(0xA0);
			
			// Read the key from the file.
			fread(keyPtr, 0xA0, 1, filePtr);
			
			// Close the file.
			fclose(filePtr);
			
			/*
				As specified in 'grabRSAKeysToFile',
				this is for compatibility with C99.
			*/
			int i;

			for (i = 0; i < 4; i++)
			{
				memcpy((void*)(RSAaddr + (0xA0 * i)), keyPtr, 0xA0);
			}
			
			// Free the key.
			free(keyPtr);
		#endif
	}
	
	// Return the default response.
	return TRUE;
}

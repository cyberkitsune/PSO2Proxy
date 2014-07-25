
SRCS+=dllmain.c

DLLS=rsainject.dll dumper.dll


#Default Warnings Flags
WFLAGS:=-Wall -W (WFLAGS)

#Default Compiler Flags
CFLAGS:=-Os -Wall -W $(CFLAGS) -x c

#Default Linker Flags
LDFLAGS+=-shared -s

#local compiler or use a cross-compiler
#PREFIX=i686-w64-mingw32
ifdef PREFIX
CC=$(PREFIX)-gcc
else
# We really do need this. Note that overriding this on the command-line still
# works: see section 9.5 of the make manual.
CC=gcc
endif

#Hide commands by default
ifndef V
AT:=@
endif

all: $(SRCS) $(DLLS)

rsainject.dll: $(SRCS)
	$(AT) $(CC) $(CFLAGS) -UDUMPER $< $(LDFLAGS) -o $@

dumper.dll: $(SRCS)
	$(AT) $(CC) $(CFLAGS) -DDUMPER $< $(LDFLAGS) -o $@

 .PHONY : clean   # .PHONY ignores files named clean
clean:
	-$(AT) $(RM) $(DLLS)

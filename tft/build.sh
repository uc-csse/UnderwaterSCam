gcc -c rgb888_to_rgb565.c 
gcc -shared -Wl,-soname,rgb888_to_rgb565.so -o rgb888_to_rgb565.so rgb888_to_rgb565.o

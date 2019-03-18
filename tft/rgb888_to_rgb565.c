//gcc -shared -o rgb888_to_rgb565.so rgb888_to_rgb565.c   
unsigned long RGB888_to_RGB565(char* in_rgb, char* out_565,long total)
{
  for (int i=0;i<total;i++)
  {
    char r,g,b;
    b=in_rgb[i*3];
    g=in_rgb[i*3+1];
    r=in_rgb[i*3+2];
    
    unsigned short* po=(unsigned short*)(out_565+i*2);
    *po=(((r&0xF8)<<8)|((g&0xFC)<<3)|((b&0xF8)>>3));
  }
}

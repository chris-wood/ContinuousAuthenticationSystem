/*
 * File: keymap.h
 * Description: This file contains the scancode->keyboard character
 *              map that is used to convert hardware scancodes to their
 *              ASCII equivalent. It is based off of the US keyboard layout
 * Author: Christopher A. Wood, caw4567@rit.edu
 */
 
/* Begin Klog code */
#define INVALID 0X00   //scan code not supported by this driver
#define SPACE 0X01     //space bar
#define ENTER 0X02     //enter key
#define LSHIFT 0x03    //left shift key
#define RSHIFT 0x04    //right shift key
#define CTRL  0x05     //control key
#define ALT	  0x06     //alt key
 
char scancodeMap[84] = {
INVALID, //0
INVALID, //1
'1', //2
'2', //3
'3', //4
'4', //5
'5', //6
'6', //7
'7', //8
'8', //9
'9', //A
'0', //B
'-', //C
'=', //D
INVALID, //E
INVALID, //F
'q', //10
'w', //11
'e', //12
'r', //13
't', //14
'y', //15
'u', //16
'i', //17
'o', //18
'p', //19
'[', //1A
']', //1B
ENTER, //1C
CTRL, //1D
'a', //1E
's', //1F
'd', //20
'f', //21
'g', //22
'h', //23
'j', //24
'k', //25
'l', //26
';', //27
'\'', //28
'`', //29
LSHIFT,	//2A
'\\', //2B
'z', //2C
'x', //2D
'c', //2E
'v', //2F
'b', //30
'n', //31
'm' , //32
',', //33
'.', //34
'/', //35
RSHIFT, //36
INVALID, //37
ALT, //38
SPACE, //39
INVALID, //3A
INVALID, //3B
INVALID, //3C
INVALID, //3D
INVALID, //3E
INVALID, //3F
INVALID, //40
INVALID, //41
INVALID, //42
INVALID, //43
INVALID, //44
INVALID, //45
INVALID, //46
'7', //47
'8', //48
'9', //49
INVALID, //4A
'4', //4B
'5', //4C
'6', //4D
INVALID, //4E
'1', //4F
'2', //50
'3', //51
'0', //52
};

/* End Klog code */

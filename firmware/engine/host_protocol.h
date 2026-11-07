/**
 * Tape Master v2 - USB CDC Host Communication Protocol
 * 
 * High-speed bidrectional command & streaming protocol over USB Serial.
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef HOST_PROTOCOL_H
#define HOST_PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Stream Packet Header Magic for binary pulse stream
#define PROTOCOL_STREAM_MAGIC   0xAA55

typedef enum {
    STREAM_MODE_DISABLED = 0,
    STREAM_MODE_PULSES   = 1,   // Streams captured pulse intervals in microseconds
    STREAM_MODE_RAW_ADC  = 2,   // Streams raw 12-bit ADC head samples
    STREAM_MODE_AZIMUTH  = 3    // Streams real-time Azimuth peak levels (100 Hz)
} stream_mode_t;

/**
 * Initialize USB serial host communication protocol.
 */
void host_protocol_init(void);

/**
 * Poll USB serial RX buffer, parse commands and dispatch actions (called from Core 0).
 */
void host_protocol_poll(void);

/**
 * Send an asynchronous event / log message to the PC host.
 * Format: "EVENT:<NAME> <ARG>\r\n"
 */
void host_protocol_send_event(const char *event_name, const char *arg);

/**
 * Push captured pulse data to USB CDC stream (called when STREAM_MODE_PULSES is active).
 */
void host_protocol_stream_pulse(uint32_t interval_us);

/**
 * Push raw ADC sample to USB CDC stream.
 */
void host_protocol_stream_adc(uint16_t sample_raw);

/**
 * Check if active streaming is enabled by host.
 */
bool host_protocol_is_streaming(void);

/**
 * Get current stream mode.
 */
stream_mode_t host_protocol_get_stream_mode(void);

#ifdef __cplusplus
}
#endif

#endif // HOST_PROTOCOL_H

cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake OPTIONAL)

project(tape_master_v2 C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(tape_master_v2
    main.c
    drivers/tlc5916_leds.c
    drivers/cartridge_id.c
    drivers/buttons.c
    drivers/encoder.c
    drivers/oled_display.c
    drivers/analog_frontend.c
    drivers/motor_control.c
    drivers/sd_card.c
    drivers/fat_fs.c
    formats/tap_c64.c
    formats/tzx_spectrum.c
    formats/csw_raw.c
    engine/virtual_deck.c
    engine/signal_digitizer.c
    engine/exerciser_engine.c
    ui/ui_menu.c
)

# Generate C headers from PIO assembly sources
pico_generate_pio_header(tape_master_v2 ${CMAKE_CURRENT_LIST_DIR}/pio/pulse_timer_rx.pio)
pico_generate_pio_header(tape_master_v2 ${CMAKE_CURRENT_LIST_DIR}/pio/pulse_gen_tx.pio)
pico_generate_pio_header(tape_master_v2 ${CMAKE_CURRENT_LIST_DIR}/pio/audio_pwm_tx.pio)

target_include_directories(tape_master_v2 PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_CURRENT_LIST_DIR}/config
    ${CMAKE_CURRENT_LIST_DIR}/drivers
    ${CMAKE_CURRENT_LIST_DIR}/formats
    ${CMAKE_CURRENT_LIST_DIR}/engine
    ${CMAKE_CURRENT_LIST_DIR}/ui
    ${CMAKE_CURRENT_LIST_DIR}/pio
)

target_link_libraries(tape_master_v2
    pico_stdlib
    pico_multicore
    hardware_pio
    hardware_dma
    hardware_i2c
    hardware_spi
    hardware_adc
    hardware_clocks
)

# Enable USB serial output and disable UART stdio by default
pico_enable_stdio_usb(tape_master_v2 1)
pico_enable_stdio_uart(tape_master_v2 0)

pico_add_extra_outputs(tape_master_v2)

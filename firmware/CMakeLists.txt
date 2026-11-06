cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake OPTIONAL)

project(tape_master C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(tape_master
    main.c
)

pico_generate_pio_header(tape_master ${CMAKE_CURRENT_LIST_DIR}/c2n_rx.pio)
pico_generate_pio_header(tape_master ${CMAKE_CURRENT_LIST_DIR}/c2n_tx.pio)
pico_generate_pio_header(tape_master ${CMAKE_CURRENT_LIST_DIR}/zx_audio.pio)

target_link_libraries(tape_master
    pico_stdlib
    pico_multicore
    hardware_pio
    hardware_dma
    hardware_i2c
    hardware_spi
)

pico_add_extra_outputs(tape_master)

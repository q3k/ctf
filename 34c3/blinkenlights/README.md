Blinkenlights
=============

You were given a firmware and CSV dump (seemingly from a logic analyzer). After some digging, you could figure out that it was a STM32F4 micro driving WS2812B LEDs in a 16x16 matrix.

What follows is a decoder of the protocol that dumps the frames into a binary file and a pygame tool that draws them.

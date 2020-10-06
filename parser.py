import struct
import logging
import time


TOKEN_START   = 0xFE
TYPE_PO_PARAM = 0x55
TYPE_PO_WAVE  = 0x56

LEN_PO_PARAM = 10
LEN_PO_WAVE = 8

INVALID_PR = 511
INVALID_SPO2 = 127 
INVALID_PI = 0

# Examples:
# FE 08 56 1F 00 05 22 A4
# FE 0A 55 00 4F 63 14 BF 39 1D

def to_signed_short(low, high):
    return struct.unpack('h', bytearray([low, high]))[0]

class ParseException(Exception): pass

class Parser:
    def calc_msg_len(self, start):
        if len(start) < 2:
            return 0

        if start[0] == TOKEN_START and start[1] in (LEN_PO_PARAM, LEN_PO_WAVE):
            return start[1]

        return 0

    def parse(self, raw):    
        if len(raw) < LEN_PO_WAVE:
            raise ParseException(f'message too short: {raw.hex()}')

        if not self.calc_msg_len(raw):
            raise ParseException(f'start token missing/invalid: {raw.hex()}')
        
        if raw[2] == TYPE_PO_WAVE:
            return self.parse_wave(raw)
        elif raw[2] == TYPE_PO_PARAM:
            return self.parse_param(raw)
                
        raise ParseException(f'unknown message: {raw.hex()}')

    def parse_wave(self, raw):
        data = raw[3]
        spo2_wave_val = raw[5]
        sensor_off = bool((raw[4] >> 1) & 1)

        counter = raw[6]
        unknown1 = raw[4]
        unknown2 = raw[7]

        return dict(type='wave', unknown_1=unknown1, unknown_2=unknown2, counter=counter, ppg=data, spo2_wave_val=spo2_wave_val, sensor_off=sensor_off, parse_time=time.time())

    def parse_param(self, raw):
        pr = to_signed_short(raw[4], raw[3])
        spo2 = raw[5]
        pi = to_signed_short(raw[7], raw[6])
        counter = raw[8]
        unknown1 = raw[9]
        
        # check for invalid values
        if pr == INVALID_PR:
            pr = None
            
        if spo2 == INVALID_SPO2:
            spo2 = None

        if pi == INVALID_PI:
            pi = None
            
        return dict(type='param', unknown_1=unknown1, pulse_rate=pr, spo2=spo2, counter=counter, perfusion_index=pi / 1000, parse_time=time.time())
    
 
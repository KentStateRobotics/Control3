#!/usr/bin/env python
'''
messages
KentStateRobotics Jared Butcher 7/21/2019

Message Types:
    Struct Types:
        Format  C-Type              Python-Type     Size
        x       pad byte            NA              1
        c       char                bytes           1
        b       signed char         int             1
        B       unsigned char       int             1
        ?       bool                bool            1
        h       short               int             2
        H       unsigned short      int             2
        i       int                 int             4
        I       unsigned int        int             4
        l       long                int             4
        L       unsigned long       int             4
        q       long long           int             8
        Q       unsigned long long  int             8
        e       half                float           2
        f       float               float           4
        d       double              float           8
        s       char[]              bytes           Fixed size n used as "ns"
        p       char[]              bytes           <= 255 Pascal string sized n used as "np"
    Variable Length Types:
        blob    char[]              bytes           variable
'''
from . import message

SubscriberMsg = message.Message({
    'source': str(message.NAME_LENGTH) + 's',
    'topic': str(message.NAME_LENGTH) + 's',
    'remove': '?'
})
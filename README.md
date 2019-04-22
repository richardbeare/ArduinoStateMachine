# ArduinoStateMachine
My setup to use QuantumLeaps hierarchical state machine software for Arduino, under linux.

## Background

The hierchical state machine, decribed by Miro Samek, is a great
framework for developing embedded systems. There is a steep learning
curve when starting from a traditional programming background, but it
is definitely the way to go if your application has anything remotely
asynchronous about it - e.g. emergency stop switches.

There are several pieces of software, distributed by
[QuantumLeaps](http://www.state-machine.com/) that work together
to make this possible with Arduino microcontrollers. However,
Arduino isn't an area of focus for QuantumLeaps, so there's a
bit of effort required to produce a working development environment,
especially under linux.

When I first looked into this, back in 2014, there was more Arduino
support. Now the only framework from QuantumLeaps with Arduino tools
appears to be the "Nano" framework. Not yet sure how this differs from
what I used before, but does mean I need to start again.

This repository contains my recipes.

## Platform

Linux Mint.

Arduino Uno.

## Dependencies

1. The [Arduino tools](https://www.arduino.cc).
1. The _qp-nano_
   [framework](https://github.com/QuantumLeaps/qpn-arduino). This is
   the event driven framework for Arduino. (a submodule in this repo)
1. QM from [here](https://github.com/QuantumLeaps/qm/releases). QM is
   the graphical tool used to create an event driven application.
1. The [Arduino-Makefile](https://github.com/sudar/Arduino-Makefile) (a submodule of this repo)

Fetching these should provide you with _arduino-1.8.6-linux64.tar.xz_,
_qm\_4.3.0-linux64_, a _qpn-arduino_ folder hierarchy and an _Arduino-Makefile_ hiearchy.

## Installation

* Extract the arduino tools and run to ensure that a sketch folder hiearchy is available:

``` bash
./arduino-1.8.6/arduino
```

The default sketch folder is `${HOME}/Arduino`. In theory it can be changed, but I haven't
bothered.

* Install QM:

```bash
chmod +x qm_4.3.0-linux64
./qm_4.3.0-linux64
```

This installs into `${HOME}/qm`, and it doesn't appear to be possible
to change during installation with the current setup.

* copy the qpn library into the sketch folder:

``` bash
rsync -av qpn-arduino/ ~/Arduino/
```

## Testing

Qpn comes with a led blinking application. It is in
`Arduino/libraries/qpn_avr/examples/blinky/`. The default configuration
utilises a tclsh build system, with lots of windows and mac dependencies. It
appears simpler to replace with the Arduino-Makefile structure. There's a blinky
folder in this repo containing a skeleton Makefile. There are a bunch of environment
variables that need to be set based on where this repo has been placed. Adjust them and
copy the Makefile to `~/Arduino/libraries/qpn_avr/examples/blinky/`

The Makefile setup has a lot of options. Only the basics here to get started.

Note that `ARDUINO_LIBS` includes _qpn\_avr_ so that the framework is included in the
build.

Fire up qm:

```bash
~/qm/bin/qm.sh
```

Open the blinky project (navigate to `~/Arduino/libraries/qpn_avr/examples/blinky/blinky.qm`).

Select Tools->Manage External Tools

For each of the "build", "clean"  and "upload" options, use "make" in
the command field and "all", "clean" and "upload" in the argument
field.

Click the build and upload icons and confirm that everything is working.

The environment variables at the top of the management dialog don't
appear useful anymore. This sort of thing is now handled by the
makefile.

Use "make monitor" to see the serial output.

### QM foibles

QM seems to save state in a .projectname file. This includes the external tool and
environment variable configuration.

## Documentation links

[QP-Nano](http://www.state-machine.com/qpn/)

[Getting started with QP-Nano](https://www.state-machine.com/doc/AN_Getting_Started_with_QP-nano.pdf)

[Crash course in UML state machines](https://state-machine.com/doc/AN_Crash_Course_in_UML_State_Machines.pdf)

## Timer frequency

There's some board configuration stuff burried in `QF_onStartup`. In the blinky example these settings are as follows:

```c
void QF_onStartup(void) {
    // set Timer2 in CTC mode, 1/1024 prescaler, start the timer ticking...
    TCCR2A = (1U << WGM21) | (0U << WGM20);
    TCCR2B = (1U << CS22 ) | (1U << CS21) | (1U << CS20); // 1/2^10
    ASSR  &= ~(1U << AS2);
    TIMSK2 = (1U << OCIE2A); // enable TIMER2 compare Interrupt
    TCNT2  = 0U;

    // set the output-compare register based on the desired tick frequency
    OCR2A  = (F_CPU / BSP_TICKS_PER_SEC / 1024U) - 1U;
}
```

Explanations [https://sites.google.com/site/qeewiki/books/avr-guide/pwm-on-the-atmega328]. 
[http://maxembedded.com/2011/07/avr-timers-ctc-mode/]

This lines sets CTC mode - "clear timer on compare". The same registers are also 
used in pulse width modulation applications.
```c
    TCCR2A = (1U << WGM21) | (0U << WGM20);
```

These lines set the clock frequency division. High divisions for low power applications, 
like blinky
```c
TCCR2B = (1U << CS22 ) | (1U << CS21) | (1U << CS20); // 1/2^10
TCCR2B = (1U << CS22 ) | (1U << CS21) | (0U << CS20); // 1/256
TCCR2B = (1U << CS22 ) | (0U << CS21) | (1U << CS20); // 1/128
TCCR2B = (1U << CS22 ) | (0U << CS21) | (0U << CS20); // 1/64
TCCR2B = (0U << CS22 ) | (1U << CS21) | (1U << CS20); // 1/32
TCCR2B = (0U << CS22 ) | (1U << CS21) | (0U << CS20); // 1/8
TCCR2B = (0U << CS22 ) | (0U << CS21) | (1U << CS20); // no prescaling

```

Finally, the output compare register (OCR) is set.
```c
    OCR2A  = (F_CPU / 1024U / BSP_TICKS_PER_SEC) - 1U;
```

A timer will fire when the number of ticks (after frequency division) reaches the OCR value.

The `F_CPU/1024U` component of the equation is the number of ticks in one second, if using the 
setting for scaling by 1024. 

The combination of divisor and `BSP\_TICKS\_PER\_SEC` needs to be
selected so that the value for OCR2A is between 0 and 255.

There appear to be 4 timers available in qpn. They are defined in _qpn.h_ as `Q\_TIMEOUT\_SIG`, `Q\_TIMEOUT1\_SIG`, etc. They are activated with calls like:


Seems that the OCR2A register is 8 bit
```c
QActive_armX((QActive *)me, /* object pointer */
             0U,            /* which timeout - Q_TIMEOUT_SIG, Q_TIMEOUT1_SIG etc */
             BSP_TICKS_PER_SEC/2U, /* number of ticks for rearming - seems to be for the first firing only.  */
             BSP_TICKS_PER_SEC/100U); /* interval between ticks */

```

## Input debouncing

Switch bounce needs to be dealt with before hitting the state
machines. There's various discussion of this around, but I can't find
the original source I used. Here's the code I use for 4 inputs - 2
optical and 2 manual switches. The idea is to use the interrupt
service routine (ISR) to do the debouncing. The ISR is called every
time the system clock (set up above) ticks. Events are transmitted
back to QF objects using `QACTIVE\_POST\_ISR`. The code below is set
up to test inputs every `TicksPerISR` clock ticks. The idea is that
high speed driving of a stepper motor is controlled by the master clock, but the
switches are slower, so we don't need to check them as often.

The port numbers are defined in an enum. The connections of interest
are defined in the `B00111100` pattern - in this case pins 2,3,4,5. We
ignore pins 0 and 1 because they are used for serial IO on Arduino.

```c
ISR(TIMER2_COMPA_vect) {
    QF_tickXISR(0); // process time events for tick rate 0

    // No need to clear the interrupt source since the Timer2 compare
    // interrupt is automatically cleard in hardware when the ISR runs.

    // optical home needs to fire on a low->high transition
    // advance could be on either transition.
    // both need to be on transition, otherwise we flood the event queues
    // Might be best to have another, slower ISR for buttons, or only check them every 10th
    // entry to this loop

    static uint8_t interruptCounter = 0;
    // need to sort this out - probably want to arrange for firing on button release
    static uint8_t nOld=0;   /* previous-previous switch bitmask */
    static uint8_t nPrev=0;  /* previous  switch bitmask */
    static uint8_t nOutput=0; /* debounced switch bitmaks */
    static uint8_t pOutput=0;
    ++interruptCounter;
    if (interruptCounter == TicksPerISR) {
       // only check the switches every 10 clock ticks
       interruptCounter = 0;F_CPU 
       // do the low frequency stuff, like button checks

       // read AND debounce all the switches
       /* read the current state of the switches, ignoring
        the serial port pins. all the inputs need to be on
        PORTD (pins 0 to 7) */
        // B00111100 needs to match the input pins defined at the top. i.e we
        // want 2,3,4,5. Leave 0 and 1 alone - they are for serial IO.
        uint8_t nCurrent = PIND & B00111100;
        nOutput = (nOutput & (nOld | nPrev | nCurrent)) |
                             (nOld & nPrev & nCurrent);
        nOld = nPrev;
        nPrev = nCurrent;


        // compare  nOutput and pOutput to get a transition
        // low to high transitions only
        uint8_t LowtoHigh = nOutput & (~pOutput);
        /* the following relies on the input ports being PIN numbers 0-7 */
        uint8_t opticalA = LowtoHigh & (1 << OPTICAL_A);
        uint8_t opticalB = LowtoHigh & (1 << OPTICAL_B);
        uint8_t buttonA = LowtoHigh & (1 << BUTTON_A);
        uint8_t buttonB = LowtoHigh & (1 << BUTTON_B);
        pOutput=nOutput;

        if (opticalA) {
           BSP_Debug("Optical A");
           QACTIVE_POST_ISR((QMActive *)&AO_Stepper, OPTICAL_A_SIG, 0U);
        }
        if (opticalB) {
           BSP_Debug("Optical B");
           QACTIVE_POST_ISR((QMActive *)&AO_Stepper, OPTICALSTOP_A_SIG, 0U);
        }

        if (buttonA) {
            BSP_Debug("Button A");
            QACTIVE_POST_ISR((QMActive *)&AO_Stepper, BUTTONPRESS_A_SIG, 0U);
        }

        if (buttonB) {
            BSP_Debug("Button B");
            QACTIVE_POST_ISR((QMActive *)&AO_Stepper, BUTTONPRESS_B_SIG, 0U);
        }

   }

}

```

Care needs to be taken when defining the signals sent by the post function:
```c
enum InputSignals {
OPTICALSTOP_A_SIG=Q_USER_SIG, // Vital that the value for the first signal is set correctly.
OPTICALSTOP_B_SIG, 
BUTTONPRESS_A_SIG, 
BUTTONPRESS_B_SIG
};

```

## Other notes

The _bsp_ files (board support package?) are important if you want to
do things like drive stepper motors at decent speeds, and for
including code to debounce switches.

# Linux versions

Is it possible to test designs with the posix tools? Seems there is a posix port, so lets give it
a go.

[qpn, not for arduino](https://github.com/QuantumLeaps/qpn/releases)

unzip it. There are examples for each backend. Linux stuff in `qpn/examples/posix-qv/`.

_Pelican_ doesn't compile, _blinky_ and _dpp_ do.

Figure out a qm version?

This seems to work. Copy the arduino qm blinky project and replace the various .c, .h files with ones
from the blinky posix project. Don't replace blinky.c or blinky.h - they come from the qm interface.

Very likely to be a good option for testing designs.


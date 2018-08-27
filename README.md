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

For each of the "build", "clean" and "upload" options, use "make" in
the command field and "all", "clean" and "upload" in the argument
field.

Click the build and upload icons and confirm that everything is working.

The environment variables at the top of the management dialog don't
appear useful anymore. This sort of thing is now handled by the
makefile.

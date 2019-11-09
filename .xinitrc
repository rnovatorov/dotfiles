#!/bin/sh

# start some nice programs
if [ -d /etc/X11/xinit/xinitrc.d ]; then
    for f in /etc/X11/xinit/xinitrc.d/?*.sh; do
        [ -x "$f" ] && . "$f"
    done
    unset f
fi

# disable touchpad
touchpad off

# syncronize clipboards
parcellite --no-icon &

# start wm
exec i3

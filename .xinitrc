#!/bin/sh

# start some nice programs
if [ -d /etc/X11/xinit/xinitrc.d ]; then
    for f in /etc/X11/xinit/xinitrc.d/?*.sh; do
        [ -x "$f" ] && . "$f"
    done
    unset f
fi

# configure DPI
xrandr --dpi 96

# configure keyboard repeat rate and delay
xset r rate 300 50

# set compose key
setxkbmap -option compose:ralt

# disable touchpad
touchpad off

# syncronize clipboards
parcellite --no-icon &

# xss-lock grabs a logind suspend inhibit lock and will use i3lock to lock the
# screen before suspend. `loginctl lock-session` is used to lock the screen.
xss-lock --transfer-sleep-lock -- i3lock --nofork --image ~/.wallpaper &

# set wallpaper
feh --bg-scale ~/.wallpaper

# start compositor
picom &

# start battery tray icon
cbatticon --low-level 75 --critical-level 50 &

# start wm
exec i3

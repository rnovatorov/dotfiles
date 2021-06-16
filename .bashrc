# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Set color prompt
PS1='\[\033[01;32m\]\u@\h:\[\033[01;34m\]\w\[\033[00m\]$ '

# Larger history
export HISTSIZE=5000

# Ignore identical commands in history
export HISTCONTROL=ignoredups

# Search history with arrows
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'

# Load bash aliases
if [[ -f ~/.bash_aliases ]]; then
    source ~/.bash_aliases
fi

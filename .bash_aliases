# diff
alias diff='diff --color=auto'

# grep
alias grep='grep --color=auto'

# ls
alias ls='ls --color=auto'
alias la='ls -A'
alias ll='la -l'

# dotfiles
alias config='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'

# man
man() {
    LESS_TERMCAP_mb=$'\e[1;31m' \
    LESS_TERMCAP_md=$'\e[1;33m' \
    LESS_TERMCAP_me=$'\e[0m' \
    LESS_TERMCAP_so=$'\e[1;44;32m' \
    LESS_TERMCAP_se=$'\e[0m' \
    LESS_TERMCAP_us=$'\e[1;35m' \
    LESS_TERMCAP_ue=$'\e[0m' \
    command man "$@"
}

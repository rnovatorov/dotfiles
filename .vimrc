filetype plugin indent on
syntax on
let mapleader = " "

set showmode
set showcmd
set number
set encoding=utf-8
set backspace=indent,eol,start
set clipboard=unnamedplus
set ignorecase
set smartcase
"set autoindent
set incsearch

" Enable support for russian keyboard layout
set spelllang=ru_yo,en_us
set keymap=russian-jcukenwin
set iminsert=0
set imsearch=0

" Shift motion keys to the home row
noremap ; l
noremap l k
noremap k j
noremap j h

" Use `kl` to enter command mode
inoremap kl <ESC>

" Disable arrows
"nnoremap <up> <nop>
"nnoremap <down> <nop>
"nnoremap <left> <nop>
"nnoremap <right> <nop>
"inoremap <up> <nop>
"inoremap <down> <nop>
"inoremap <left> <nop>
"inoremap <right> <nop>

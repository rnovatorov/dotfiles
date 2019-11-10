set showmode
set number
set clipboard=unnamedplus
set ignorecase
set smartcase

" Enable support for russian keyboard layout
set spelllang=ru_yo,en_us
set keymap=russian-jcukenwin
set iminsert=0
set imsearch=0

let mapleader = " "

" Set `jkl;` as a homerow
noremap h ;
noremap ; l
noremap l k
noremap k j
noremap j h

" Use `kl` to enter command mode
inoremap kl <ESC>

" Navigate windows with `jkl;`
nnoremap <C-w>h <C-w>;
nnoremap <C-w>; <C-w>l
nnoremap <C-w>l <C-w>k
nnoremap <C-w>k <C-w>j
nnoremap <C-w>j <C-w>h

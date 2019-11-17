" Show the active mode
set showmode

" Enable line numbering
set number

" Use system clipboard
set clipboard=unnamedplus

" Enable support for russian keyboard layout
set spelllang=ru_yo,en_us
set keymap=russian-jcukenwin
set iminsert=0
set imsearch=0

" Set map leader
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

" Plugins
call plug#begin()

Plug 'scrooloose/nerdtree'
Plug 'junegunn/fzf.vim'
Plug 'dense-analysis/ale'
Plug 'airblade/vim-gitgutter'
Plug 'fatih/vim-go'

call plug#end()

" Toggle NERDTree
noremap <Leader>t :NERDTreeToggle<CR>

" Run `fzf`
noremap <Leader>f :FZF<CR>
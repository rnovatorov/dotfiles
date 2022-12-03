#!/bin/bash

alacritty --class Alacritty,Shell --working-directory ~/code/enapter/monorepo &
alacritty --class Alacritty,Editor --working-directory ~/code/enapter/monorepo --command env GOFLAGS="-tags=integration,lua53" nvim &

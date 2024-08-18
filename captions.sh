#!/bin/bash
##   Generates captions for images  in the current directory.
##   Copyright (C) 2024 by Henry Kroll III, www.thenerdshow.com
##
##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU General Public License as published by
##   the Free Software Foundation; either version 2 of the License, or
##   (at your option) any later version.
##
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU General Public License for more details.
##
##   You should have received a copy of the GNU General Public License along
##   with this program; if not, write to the Free Software Foundation, Inc.,
##   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

printf -- "--image %q " *.png *.gif *.webp *.webm *.jpg *.jpeg|xargs llava_phi3.sh -p "Write a caption for the image." --template '<figure><img src="[image]" alt="[[image]]"><figcaption>[description]</figcaption></figure>' -c 4096 --log-disable | tee data

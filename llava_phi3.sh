llama-llava-cli -ngl 16 --temp 0.1 -m ~/.local/share/models/llava-phi-3-mini-int4.gguf --mmproj  ~/.local/share/models/llava-phi-3-mini-mmproj-f16.gguf -c 4096 "$@"

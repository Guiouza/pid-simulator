# How to write templates

Create a file usely we use a .txt file.
The first line is the header that conteins information for how to print the asset:
The base header looks like this

``` txt
{nlines} {ncols} {win_y} {win_x} {draw_box} {text_y} {text_x} {type} ...
text to show
```

The final infomations very with the type of asset:

## Textlabel

``` txt
{type} {input_y} {input_x} {max_len} {default}
```

## Button

``` txt
{type} {cursor_y} {cursor_x}
```

## Text

Just have the type and no more information to handle
